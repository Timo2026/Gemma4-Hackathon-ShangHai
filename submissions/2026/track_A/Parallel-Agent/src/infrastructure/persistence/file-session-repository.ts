import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";

import type { SessionRepository } from "../../application/ports";
import type { SessionState } from "../../domain/types";

export class FileSessionRepository implements SessionRepository {
  constructor(
    private readonly baseDir = path.resolve(
      process.cwd(),
      process.env.PARALLEL_AGENT_SESSION_DIR ?? ".parallel-agent-data/sessions",
    ),
  ) {}

  async save(session: SessionState): Promise<void> {
    await mkdir(this.baseDir, { recursive: true });
    const filePath = this.getFilePath(session.sessionId);
    await writeFile(filePath, `${JSON.stringify(session, null, 2)}\n`, "utf8");
  }

  async load(sessionId: string): Promise<SessionState | null> {
    const filePath = this.getFilePath(sessionId);

    try {
      const content = await readFile(filePath, "utf8");
      return JSON.parse(content) as SessionState;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === "ENOENT") {
        return null;
      }

      throw error;
    }
  }

  async list(): Promise<SessionState[]> {
    await mkdir(this.baseDir, { recursive: true });
    const files = await readdir(this.baseDir);

    const sessions = await Promise.all(
      files
        .filter((file) => file.endsWith(".json"))
        .map(async (file) => {
          const content = await readFile(path.join(this.baseDir, file), "utf8");
          return JSON.parse(content) as SessionState;
        }),
    );

    return sessions.sort((a, b) => a.sessionId.localeCompare(b.sessionId));
  }

  private getFilePath(sessionId: string): string {
    return path.join(this.baseDir, `${sessionId}.json`);
  }
}
