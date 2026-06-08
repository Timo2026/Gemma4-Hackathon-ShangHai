import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.tasks import _gap_status, _measure_codes_for_document, _measure_codes_from_filename, _task_status
from app.db.session import get_session
from app.main import app
from app.models.document import Document
from app.models.extraction_result import ExtractionResult, ExtractionStatus
from app.models.measure import Measure, MeasureCode
from app.models.measure_evaluation import MeasureEvaluation
from app.services.extraction import (
    LLMExtractionError,
    UnsupportedMeasureError,
    _infer_measure_codes_from_document,
    _load_system_prompt,
    _prompt_path_for_measure,
)


class _FakeScalarResult:
    def __init__(self, items):
        self._items = items

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return list(self._items)


class _FakeExecuteResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return _FakeScalarResult(self._items)

    def all(self):
        return []


class _FakeSession:
    def __init__(self, document: Document, measures: list[Measure]):
        self.document = document
        self.measures = measures
        self.extractions: list[ExtractionResult] = []
        self.evaluations: list[MeasureEvaluation] = []
        self.added_objects: list[object] = []
        self._next_extraction_id = 1
        self._next_evaluation_id = 1
        self.rollback_called = False

    def get(self, model, value):
        if model is Document and value == self.document.id:
            return self.document
        return None

    def execute(self, statement):
        entity = statement.column_descriptions[0].get("entity")
        if entity is Document:
            return _FakeExecuteResult([self.document])
        if entity is ExtractionResult:
            return _FakeExecuteResult(list(reversed(self.extractions)))
        if entity is MeasureEvaluation:
            return _FakeExecuteResult(list(reversed(self.evaluations)))
        return _FakeExecuteResult(self.measures)

    def add(self, obj):
        self.added_objects.append(obj)
        if isinstance(obj, ExtractionResult) and obj.id is None:
            obj.id = self._next_extraction_id
            self._next_extraction_id += 1
            self.extractions.append(obj)
        if isinstance(obj, MeasureEvaluation) and obj.id is None:
            obj.id = self._next_evaluation_id
            self._next_evaluation_id += 1
            self.evaluations.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None

    def refresh(self, _obj):
        return None

    def rollback(self):
        self.rollback_called = True

    def close(self):
        return None


class PromptFileSelectionTests(unittest.TestCase):
    def test_prompt_path_for_supported_measure(self):
        path = _prompt_path_for_measure("CBP")
        self.assertTrue(str(path).endswith("backend/prompts/cbp_extraction.txt"))

    def test_prompt_path_for_unsupported_measure(self):
        with self.assertRaises(UnsupportedMeasureError):
            _prompt_path_for_measure("UNKNOWN")

    def test_load_system_prompt_from_file(self):
        prompt = _load_system_prompt("GSD")
        self.assertIn("Output JSON only", prompt)


class MeasureInferenceTests(unittest.TestCase):
    def test_infer_measure_code_from_gsd_filename(self):
        document = Document(id=1, patient_id=1, source_pdf_path="/tmp/anything.pdf", source_txt_path="/tmp/gsd_recent_a1c_fail.txt")
        self.assertEqual(_infer_measure_codes_from_document(document), ["GSD"])

    def test_infer_measure_codes_from_mmx_filename(self):
        document = Document(id=1, patient_id=1, source_pdf_path="/tmp/chart_mmx_2026.pdf", source_txt_path="/tmp/chart.txt")
        self.assertEqual(_infer_measure_codes_from_document(document), ["CBP", "BPD"])

    def test_infer_measure_code_from_uploaded_filename(self):
        self.assertEqual(_measure_codes_from_filename("John Smith_CBP.pdf"), ["CBP"])

    def test_pending_document_uses_target_measure_codes(self):
        document = Document(id=1, patient_id=1, source_pdf_path="pending", source_txt_path="pending", target_measure_codes="CBP,BPD")
        self.assertEqual(_measure_codes_for_document(_FakeSession(document, []), document, None), ["CBP", "BPD"])


class TasksExtractAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.document = Document(id=1, patient_id=101, source_pdf_path="/tmp/patient_101.pdf", source_txt_path="/tmp/patient_101.txt")

    def tearDown(self):
        app.dependency_overrides.clear()

    def _client_with(self, measure_codes: list[str], extracted_payload: dict, measure_ids: list[int] | None = None):
        if measure_ids is None:
            measure_ids = [index + 1 for index in range(len(measure_codes))]

        measures = [
            Measure(id=measure_ids[index], code=MeasureCode(code), name=f"{code} demo")
            for index, code in enumerate(measure_codes)
        ]
        fake_session = _FakeSession(document=self.document, measures=measures)
        self.fake_session = fake_session

        def _override_get_session():
            yield fake_session

        app.dependency_overrides[get_session] = _override_get_session
        payload_patch = patch("app.services.extraction.call_llm_extract", return_value=extracted_payload)
        self.mock_call_llm_extract = payload_patch.start()
        self.addCleanup(payload_patch.stop)

        return TestClient(app)

    def _client_with_llm_error(self, measure_codes: list[str], error: Exception):
        measures = [Measure(id=index + 1, code=MeasureCode(code), name=f"{code} demo") for index, code in enumerate(measure_codes)]
        fake_session = _FakeSession(document=self.document, measures=measures)
        self.fake_session = fake_session

        def _override_get_session():
            yield fake_session

        app.dependency_overrides[get_session] = _override_get_session
        payload_patch = patch("app.services.extraction.call_llm_extract", side_effect=error)
        self.mock_call_llm_extract = payload_patch.start()
        self.addCleanup(payload_patch.stop)

        return TestClient(app)

    def test_extract_cbp_pass(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 138, "diastolic": 86, "encounter_type": "Office Visit"},
                {"date": "2026-04-20", "systolic": 144, "diastolic": 92, "encounter_type": "Office Visit"},
                {"date": "2026-04-28", "systolic": 128, "diastolic": 80, "encounter_type": "ED"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["system_evaluated_result"]["measure_code"], "CBP")
        self.assertTrue(body["system_evaluated_result"]["pass_flag"])
        evidence = body["system_evaluated_result"]["evidence_payload"]
        self.assertEqual(evidence["selected_observation"]["date"], "2026-04-20")
        self.assertEqual(evidence["selected_observation"]["lowest_systolic"], 138)
        self.assertEqual(evidence["selected_observation"]["lowest_diastolic"], 86)

    def test_extract_cbp_fail(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 145, "diastolic": 92, "encounter_type": "Office Visit"},
                {"date": "2026-04-21", "systolic": 142, "diastolic": 91, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        reason_codes = body["system_evaluated_result"]["evidence_payload"]["reason_codes"]
        self.assertIn("BP_ABOVE_TARGET", reason_codes)

    def test_extract_bpd_pass(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-18", "systolic": 139, "diastolic": 89, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["BPD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["system_evaluated_result"]["measure_code"], "BPD")
        self.assertTrue(body["system_evaluated_result"]["pass_flag"])

    def test_extract_bpd_fail(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-18", "systolic": 142, "diastolic": 91, "encounter_type": "Office Visit"},
                {"date": "2026-04-19", "systolic": 145, "diastolic": 93, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["BPD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        reason_codes = body["system_evaluated_result"]["evidence_payload"]["reason_codes"]
        self.assertIn("BP_ABOVE_TARGET", reason_codes)

    def test_extract_bpd_fail_when_only_excluded_encounters(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-18", "systolic": 120, "diastolic": 80, "encounter_type": "ED"},
                {"date": "2026-04-19", "systolic": 118, "diastolic": 78, "encounter_type": "Acute Inpatient"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["BPD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        reason_codes = body["system_evaluated_result"]["evidence_payload"]["reason_codes"]
        self.assertIn("NO_VALID_BP_AFTER_EXCLUSION", reason_codes)

    def test_extract_cbp_rejects_emergency_department_alias(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-05-05", "systolic": 120, "diastolic": 80, "encounter_type": "Emergency Department - Initial Evaluation"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        evidence = body["system_evaluated_result"]["evidence_payload"]
        self.assertIn("NO_VALID_BP_AFTER_EXCLUSION", evidence["reason_codes"])
        self.assertEqual(len(evidence["rule_result"]["bp_candidates_all"]), 1)
        self.assertEqual(evidence["rule_result"]["bp_candidates_kept"], [])
        self.assertEqual(evidence["rule_result"]["bp_candidates_excluded"][0]["encounter_type"], "ED")

    def test_extract_cbp_counts_common_allowed_encounter_aliases(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 138, "diastolic": 86, "encounter_type": "Virtual visit"},
                {"date": "2026-04-21", "systolic": 136, "diastolic": 84, "encounter_type": "Remote BP Monitoring"},
                {"date": "2026-04-22", "systolic": 134, "diastolic": 82, "encounter_type": "In-person clinic visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["system_evaluated_result"]["pass_flag"])
        kept = body["system_evaluated_result"]["evidence_payload"]["rule_result"]["bp_candidates_kept"]
        self.assertEqual([item["encounter_type"] for item in kept], ["Telehealth", "Remote Monitoring", "Office Visit"])

    def test_extract_cbp_uses_allowed_encounter_when_ed_bp_is_lower(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 120, "diastolic": 80, "encounter_type": "ER visit"},
                {"date": "2026-04-21", "systolic": 144, "diastolic": 92, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        evidence = body["system_evaluated_result"]["evidence_payload"]
        self.assertIn("BP_ABOVE_TARGET", evidence["reason_codes"])
        self.assertEqual(evidence["selected_observation"]["date"], "2026-04-21")
        self.assertEqual(evidence["rule_result"]["bp_candidates_kept"][0]["encounter_type"], "Office Visit")

    def test_extract_bpd_rejects_inpatient_alias(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-19", "systolic": 118, "diastolic": 78, "encounter_type": "Hospitalization"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["BPD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        reason_codes = body["system_evaluated_result"]["evidence_payload"]["reason_codes"]
        self.assertIn("NO_VALID_BP_AFTER_EXCLUSION", reason_codes)

    def test_extract_cbp_uses_most_recent_valid_date(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-10", "systolic": 132, "diastolic": 84, "encounter_type": "Office Visit"},
                {"date": "2026-04-20", "systolic": 144, "diastolic": 92, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        selected = body["system_evaluated_result"]["evidence_payload"]["selected_observation"]
        self.assertEqual(selected["date"], "2026-04-20")

    def test_extract_cbp_same_day_combines_lowest_systolic_and_diastolic(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 130, "diastolic": 95, "encounter_type": "Office Visit"},
                {"date": "2026-04-20", "systolic": 145, "diastolic": 85, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["system_evaluated_result"]["pass_flag"])
        selected = body["system_evaluated_result"]["evidence_payload"]["selected_observation"]
        self.assertEqual(selected["lowest_systolic"], 130)
        self.assertEqual(selected["lowest_diastolic"], 85)
        self.assertEqual(selected["dos"], "2026-04-20")
        self.assertEqual(selected["conclusion_reading"], "130/85")
        self.assertEqual([reading["reading"] for reading in selected["evidence_readings"]], ["130/95", "145/85"])
        self.assertEqual([reading["date"] for reading in selected["evidence_readings"]], ["2026-04-20", "2026-04-20"])

    def test_extract_cbp_strict_less_than_threshold(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 140, "diastolic": 89, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        reason_codes = body["system_evaluated_result"]["evidence_payload"]["reason_codes"]
        self.assertIn("BP_ABOVE_TARGET", reason_codes)

    def test_extract_gsd_pass(self):
        payload = {
            "blood_pressure_readings": [],
            "a1c_readings": [
                {"date": "2026-04-10", "value": 7.2, "test_type": "HbA1c"},
                {"date": "2026-04-18", "value": 100, "test_type": "Fasting glucose"},
            ],
        }
        client = self._client_with(["GSD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["system_evaluated_result"]["pass_flag"])
        selected = body["system_evaluated_result"]["evidence_payload"]["selected_observation"]
        self.assertEqual(selected["value"], 7.2)

    def test_extract_gsd_fail_when_missing_hba1c(self):
        payload = {
            "blood_pressure_readings": [],
            "a1c_readings": [
                {"date": "2026-04-18", "value": 100, "test_type": "Fasting glucose"},
                {"date": "2026-04-19", "value": 110, "test_type": "Random glucose"},
            ],
        }
        client = self._client_with(["GSD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        evidence = body["system_evaluated_result"]["evidence_payload"]
        selected = evidence["selected_observation"]
        self.assertIsNone(selected["value"])
        self.assertTrue(selected["is_default_value"])
        self.assertEqual(selected["fallback_value"], 9.1)
        self.assertEqual(evidence["rule_result"]["missing_hba1c_default_value"], 9.1)
        reason_codes = evidence["reason_codes"]
        self.assertIn("MISSING_HBA1C_DEFAULT_FAIL", reason_codes)

    def test_extract_gsd_accepts_hba1c_alias(self):
        payload = {
            "blood_pressure_readings": [],
            "a1c_readings": [
                {"date": "2026-04-10", "value": 7.2, "test_type": "A1C"},
            ],
        }
        client = self._client_with(["GSD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["system_evaluated_result"]["pass_flag"])
        selected = body["system_evaluated_result"]["evidence_payload"]["selected_observation"]
        self.assertEqual(selected["value"], 7.2)
        self.assertFalse(selected["is_default_value"])

    def test_extract_gsd_uses_current_narrative_hba1c(self):
        payload = {
            "blood_pressure_readings": [],
            "a1c_readings": [
                {"date": "2026-04-10", "value": 7.4, "test_type": "HbA1c", "snippet": "HbA1c was 7.4% previously"},
                {"date": "2026-04-20", "value": 8.0, "test_type": "Hemoglobin A1c", "snippet": "Current HbA1c is 8.0%"},
            ],
        }
        client = self._client_with(["GSD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        evidence = body["system_evaluated_result"]["evidence_payload"]
        selected = evidence["selected_observation"]
        self.assertEqual(selected["date"], "2026-04-20")
        self.assertEqual(selected["value"], 8.0)
        self.assertIn("HBA1C_ABOVE_TARGET", evidence["reason_codes"])

    def test_extract_gsd_requires_hba1c_in_a1c_readings_not_only_nssd(self):
        payload = {
            "blood_pressure_readings": [],
            "a1c_readings": [],
            "nssd_candidates": [
                {
                    "patient_name": "Elena Rodriguez",
                    "dob": "11/12/1963",
                    "result_value": "8.0%",
                    "dos": "05/03/2026",
                    "encounter_type": "Office Visit",
                    "measure_hint": "GSD",
                    "snippet": "HbA1c: 8.0% (Collected: 05/03/2026)",
                }
            ],
        }
        client = self._client_with(["GSD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        evidence = body["system_evaluated_result"]["evidence_payload"]
        self.assertIn("MISSING_HBA1C_DEFAULT_FAIL", evidence["reason_codes"])
        self.assertIsNone(evidence["selected_observation"]["value"])

    def test_extract_gsd_uses_most_recent_hba1c(self):
        payload = {
            "blood_pressure_readings": [],
            "a1c_readings": [
                {"date": "2026-04-10", "value": 7.2, "test_type": "HbA1c"},
                {"date": "2026-04-20", "value": 8.2, "test_type": "HbA1c"},
            ],
        }
        client = self._client_with(["GSD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["system_evaluated_result"]["pass_flag"])
        selected = body["system_evaluated_result"]["evidence_payload"]["selected_observation"]
        self.assertEqual(selected["date"], "2026-04-20")
        self.assertEqual(selected["value"], 8.2)

    def test_extract_three_documents_stable_results(self):
        scenarios = [
            {
                "measure_codes": ["CBP"],
                "payload": {
                    "blood_pressure_readings": [
                        {"date": "2026-04-20", "systolic": 138, "diastolic": 86, "encounter_type": "Office Visit", "snippet": "BP 138/86 office"},
                        {"date": "2026-04-20", "systolic": 144, "diastolic": 92, "encounter_type": "Office Visit", "snippet": "BP 144/92 repeat"},
                    ],
                    "a1c_readings": [],
                },
                "expected": ("CBP", True, "2026-04-20"),
            },
            {
                "measure_codes": ["BPD"],
                "payload": {
                    "blood_pressure_readings": [
                        {"date": "2026-04-20", "systolic": 130, "diastolic": 80, "encounter_type": "ED", "snippet": "ED BP 130/80"},
                        {"date": "2026-04-21", "systolic": 142, "diastolic": 92, "encounter_type": "Office Visit", "snippet": "Office BP 142/92"},
                    ],
                    "a1c_readings": [],
                },
                "expected": ("BPD", False, "2026-04-21"),
            },
            {
                "measure_codes": ["GSD"],
                "payload": {
                    "blood_pressure_readings": [],
                    "a1c_readings": [
                        {"date": "2026-04-10", "value": 7.4, "test_type": "HbA1c", "snippet": "A1c 7.4"},
                        {"date": "2026-04-20", "value": 8.2, "test_type": "HbA1c", "snippet": "A1c 8.2"},
                        {"date": "2026-04-21", "value": 120, "test_type": "Random glucose", "snippet": "Random glucose 120"},
                    ],
                },
                "expected": ("GSD", False, "2026-04-20"),
            },
        ]

        for scenario in scenarios:
            for _ in range(2):
                client = self._client_with(scenario["measure_codes"], scenario["payload"])
                response = client.post("/api/tasks/1/extract")
                self.assertEqual(response.status_code, 200)
                body = response.json()
                result = body["system_evaluated_result"]
                measure_code, pass_flag, selected_date = scenario["expected"]
                self.assertEqual(result["measure_code"], measure_code)
                self.assertEqual(result["pass_flag"], pass_flag)
                self.assertEqual(result["evidence_payload"]["selected_observation"]["date"], selected_date)
                self.assertEqual(body["raw_extraction"]["schema_version"], "evidence.v2")

    def test_extract_single_document_supports_cbp_and_bpd(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 138, "diastolic": 86, "encounter_type": "Office Visit"},
                {"date": "2026-04-20", "systolic": 144, "diastolic": 92, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP", "BPD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["system_evaluated_results"]), 2)
        self.assertEqual(len(body["measure_evaluation_ids"]), 2)

        by_measure = {item["measure_code"]: item for item in body["system_evaluated_results"]}
        self.assertIn("CBP", by_measure)
        self.assertIn("BPD", by_measure)
        self.assertTrue(by_measure["CBP"]["pass_flag"])
        self.assertTrue(by_measure["BPD"]["pass_flag"])
        self.assertEqual(by_measure["CBP"]["evidence_payload"]["selected_observation"], by_measure["BPD"]["evidence_payload"]["selected_observation"])

    def test_document_target_measure_codes_selects_subset(self):
        self.document.target_measure_codes = "GSD"
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 138, "diastolic": 86, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [
                {"date": "2026-04-10", "value": 7.2, "test_type": "HbA1c"},
            ],
        }
        client = self._client_with(["CBP", "BPD", "GSD"], payload)
        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["system_evaluated_results"]), 1)
        self.assertEqual(body["system_evaluated_results"][0]["measure_code"], "GSD")

    def test_extract_with_measure_ids_selects_subset(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 138, "diastolic": 86, "encounter_type": "Office Visit"},
                {"date": "2026-04-20", "systolic": 144, "diastolic": 92, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [
                {"date": "2026-04-10", "value": 7.2, "test_type": "HbA1c"},
            ],
        }
        client = self._client_with(["CBP", "BPD", "GSD"], payload)
        response = client.post("/api/tasks/1/extract", json={"measure_ids": [3]})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["measure_evaluation_ids"], [1])
        self.assertEqual(len(body["system_evaluated_results"]), 1)
        self.assertEqual(body["system_evaluated_results"][0]["measure_code"], "GSD")

    def test_extract_with_invalid_measure_ids_falls_back_to_full_set(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 138, "diastolic": 86, "encounter_type": "Office Visit"},
                {"date": "2026-04-20", "systolic": 144, "diastolic": 92, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP", "BPD"], payload)
        response = client.post("/api/tasks/1/extract", json={"measure_ids": [999]})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["system_evaluated_results"]), 2)
        by_measure = {item["measure_code"]: item for item in body["system_evaluated_results"]}
        self.assertIn("CBP", by_measure)
        self.assertIn("BPD", by_measure)

    def test_extract_with_empty_measure_ids_falls_back_to_full_set(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 138, "diastolic": 86, "encounter_type": "Office Visit"},
                {"date": "2026-04-20", "systolic": 144, "diastolic": 92, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP", "BPD"], payload)
        response = client.post("/api/tasks/1/extract", json={"measure_ids": []})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["system_evaluated_results"]), 2)
        by_measure = {item["measure_code"]: item for item in body["system_evaluated_results"]}
        self.assertIn("CBP", by_measure)
        self.assertIn("BPD", by_measure)

    def test_extract_records_failed_attempt_when_llm_request_fails(self):
        client = self._client_with_llm_error(["CBP"], LLMExtractionError("network timeout"))

        response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 502)
        self.assertTrue(self.fake_session.rollback_called)
        self.assertEqual(len(self.fake_session.extractions), 1)
        failed_extraction = self.fake_session.extractions[0]
        self.assertEqual(failed_extraction.status, ExtractionStatus.FAILED)
        self.assertFalse(failed_extraction.is_valid)
        self.assertEqual(failed_extraction.extracted_payload["error_message"], "network timeout")

        detail_response = client.get("/api/tasks/1")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["status"], "PENDING")

    def test_extract_rejects_confirmed_task(self):
        payload = {
            "blood_pressure_readings": [
                {"date": "2026-04-20", "systolic": 138, "diastolic": 86, "encounter_type": "Office Visit"},
            ],
            "a1c_readings": [],
        }
        client = self._client_with(["CBP"], payload)
        confirmed_evaluation = MeasureEvaluation(
            id=9,
            patient_id=self.document.patient_id,
            measure_id=1,
            document_id=self.document.id,
            extraction_result_id=3,
            pass_flag=True,
            evidence_payload={"is_confirmed": True},
        )

        with patch("app.api.tasks._latest_evaluation", return_value=confirmed_evaluation):
            response = client.post("/api/tasks/1/extract")

        self.assertEqual(response.status_code, 409)
        self.mock_call_llm_extract.assert_not_called()


class TaskStatusTests(unittest.TestCase):
    def test_task_status_ignores_failed_attempt_for_task_level_status(self):
        failed_extraction = ExtractionResult(
            id=1,
            patient_id=1,
            document_id=1,
            status=ExtractionStatus.FAILED,
            extracted_payload={"error_message": "timeout"},
            model_name="demo",
            is_valid=False,
        )
        evaluation = MeasureEvaluation(
            id=2,
            patient_id=1,
            measure_id=1,
            document_id=1,
            extraction_result_id=1,
            pass_flag=True,
            evidence_payload={"selected_observation": {}},
        )

        self.assertEqual(_task_status(failed_extraction, None), "PENDING")
        self.assertEqual(_task_status(failed_extraction, evaluation), "EXTRACTED")

    def test_task_status_keeps_unconfirmed_linked_suggestion_pending(self):
        suggested_evaluation = MeasureEvaluation(
            id=2,
            patient_id=1,
            measure_id=1,
            document_id=1,
            extraction_result_id=1,
            pass_flag=True,
            evidence_payload={"is_suggested": True},
        )

        self.assertEqual(_task_status(None, suggested_evaluation), "PENDING")

    def test_gap_status_is_closed_only_for_confirmed_closed_decision(self):
        evaluation = MeasureEvaluation(
            id=2,
            patient_id=1,
            measure_id=1,
            document_id=1,
            extraction_result_id=1,
            pass_flag=True,
            evidence_payload={"is_confirmed": True, "reviewer_conclusion": {"decision": "GAP_CLOSED"}},
        )

        self.assertEqual(_gap_status(evaluation), "Closed")

    def test_gap_status_defaults_to_open_when_not_confirmed(self):
        pending_evaluation = MeasureEvaluation(
            id=2,
            patient_id=1,
            measure_id=1,
            document_id=1,
            extraction_result_id=1,
            pass_flag=True,
            evidence_payload={},
        )
        needs_follow_up = MeasureEvaluation(
            id=3,
            patient_id=1,
            measure_id=1,
            document_id=1,
            extraction_result_id=1,
            pass_flag=True,
            evidence_payload={"is_confirmed": True, "reviewer_conclusion": {"decision": "NEEDS_FOLLOW_UP"}},
        )
        failed_evaluation = MeasureEvaluation(
            id=4,
            patient_id=1,
            measure_id=1,
            document_id=1,
            extraction_result_id=1,
            pass_flag=False,
            evidence_payload={"is_confirmed": True, "reviewer_conclusion": {"decision": "GAP_OPEN"}},
        )

        self.assertEqual(_gap_status(None), "Open")
        self.assertEqual(_gap_status(pending_evaluation), "Open")
        self.assertEqual(_gap_status(needs_follow_up), "Open")
        self.assertEqual(_gap_status(failed_evaluation), "Open")


if __name__ == "__main__":
    unittest.main()
