// --- TEST SCRIPT START ---
import { callAIProcess } from '../utils/request';
import { agentService } from '../services/gemma4_agent_service';

async function runTestScenario() {
    console.log("=======================================");
    console.log("🚀 Running Gemma 4 Agent Service Test");
    console.log("=======================================");

    // ============= Scenario 1: Text-only Query (Function Calling Demonstration) =============
    const query1 = "帮我查找一下商品A的最新价格，并记录这次查询操作。";
    console.log(`\n[TEST] === Running Test Case 1: Text Search ('${query1}') ===`);
    let result1 = await callAIProcess(query1);
    console.log("\n[FINAL RESULT 1]");
    alert("Test Result 1:\n" + result1);

    // ============= Scenario 2: Multimodal Query (Image Processing Demonstration) =============
    const query2 = "请根据这张收据图片，帮我总结一下购买的商品和总费用。";
    // 模拟一张收据图片的URL
    const imageData = { type: 'image', dataUrl: 'http://example.com/images/receipt_sample.jpg' };

    console.log(`\n[TEST] === Running Test Case 2: Multimodal Input ('${query2}') ===`);
    let result2 = await callAIProcess(query2, imageData);
    console.log("\n[FINAL RESULT 2]");
    alert("Test Result 2:\n" + result2);

    // ============= Scenario 3: Combined Query (Text + Multimodal) =============
    const query3 = "帮我查找产品信息，同时结合图片上的数据进行全面分析。";
     console.log(`\n[TEST] === Running Test Case 3: Combined Input ('${query3}') ===`);
    let result3 = await callAIProcess(query3, imageData);
    console.log("\n[FINAL RESULT 3]");
    alert("Test Result 3:\n" + result3);

    console.log("\n=======================================");
    console.log("✅ All test scenarios completed successfully.");
}

runTestScenario();
// --- TEST SCRIPT END ---