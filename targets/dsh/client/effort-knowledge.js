/**
 * Reasoning-effort knowledge base — copied data, not hand-written.
 *
 * Upstream:  dsh-better-reasoning-effort v0.3.9
 * Upstream URL: https://github.com/HaoyueQin/dsh-better-reasoning-effort
 * Licence:   MIT (Copyright (c) 2026 HaoyueQin)
 * Extracted: 2026-09-18
 * Command:   node .superpowers/sdd/2026-09-12-review-model-config/extract-effort-knowledge.mjs --write --embed
 *
 * The table below is that plugin's `KNOWLEDGE_BASE`, extracted mechanically
 * from its published bundle (version 0.3.9, MIT). Each entry keeps
 * its upstream `note` field, which carries the official-source citation the
 * claim rests on; nothing is paraphrased, and the only rewriting is numeric
 * (`384e3` -> `384000`) and boolean (`!0` -> `true`) literal normalisation
 * done by JSON serialization.
 *
 * The same two sentinel regions are embedded in `client.js`, because the
 * browser bundle is loaded through the shell's client module table and can
 * require platform specifiers only — never a sibling file. A data module the
 * card cannot load would be decoration, so `tests/test_dsh_effort_knowledge.py`
 * compares the embedded regions with these byte for byte.
 *
 * Upstream licence text is reproduced in this package's `LICENSE` under
 * "Third-party notices".
 */

/** The copied table: upstream provenance, the level order, and every entry. */
export const EFFORT_KNOWLEDGE =
/* CK-EFFORT-KNOWLEDGE:BEGIN */
{
  "upstream": {
    "name": "dsh-better-reasoning-effort",
    "version": "0.3.9",
    "url": "https://github.com/HaoyueQin/dsh-better-reasoning-effort",
    "license": "MIT",
    "copyright": "Copyright (c) 2026 HaoyueQin",
    "extracted": "2026-09-18",
    "command": "node .superpowers/sdd/2026-09-12-review-model-config/extract-effort-knowledge.mjs --write --embed"
  },
  "levels": [
    "off",
    "minimal",
    "low",
    "medium",
    "high",
    "xhigh",
    "max"
  ],
  "entries": [
    {
      "id": "deepseek-v4-vision",
      "patterns": [
        "deepseek-v4-flash-vision",
        "deepseek-v4-vision"
      ],
      "efforts": {
        "off": "none",
        "low": "low",
        "high": "high",
        "max": "max"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "deepseek",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1048576,
      "maxTokens": 384000,
      "note": "DeepSeek \u89c6\u89c9\u5b9e\u9a8c\u7248 id\uff08deepseek-v4-flash-vision-exp\uff09\u3002\u5b98\u65b9\u76ee\u5f55\u5df2\u6807\u6ce8\u8be5\u6a21\u578b\u9000\u5f79\uff0c\u540d\u5b57\u4ecd\u88ab\u63a5\u53d7\u3001\u7531\u73b0\u884c deepseek-flash \u63d0\u4f9b\u670d\u52a1\u2014\u2014\u56fe\u7247\u8f93\u5165\u73b0\u5df2\u7531 deepseek-flash \u539f\u751f\u63d0\u4f9b\u3002"
    },
    {
      "id": "deepseek-v4",
      "patterns": [
        "deepseek-v4",
        "deepseek-flash"
      ],
      "efforts": {
        "off": "none",
        "low": "low",
        "high": "high",
        "max": "max"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "deepseek",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "contextWindow": 1048576,
      "maxTokens": 384000,
      "note": "DeepSeek \u5b98\u65b9\u679a\u4e3e Low / High / Max\uff08\u9ed8\u8ba4 High\uff1bminimal\u3001medium\u3001xhigh \u517c\u5bb9\u6620\u5c04\uff0cultra\u2192max\uff09\uff0cOff \u5373 thinking:\"disabled\"\uff08Responses API \u4e0b off \u4ee5 reasoning.effort:\"none\" \u8868\u793a\uff09\u3002\u5b98\u65b9\u6a21\u578b\u73b0\u4e3a deepseek-flash\uff08= DeepSeek-V4.1-Flash\uff0c2026-09-10 \u53d1\u5e03\uff0c25 \u4e07\u5e76\u53d1\u3001\u539f\u751f\u56fe\u7247\u8f93\u5165\uff09\u4e0e deepseek-v4-pro\uff08= DeepSeek-V4-Pro-0813\uff0c2026-09-14 \u8d77\u8bf7\u6c42\u5168\u91cf\u8def\u7531\u5230 V4.1-Flash\u3001\u4e0d\u652f\u6301\u56fe\u7247\uff09\uff1bdeepseek-v4-flash \u4e0e deepseek-v4-flash-vision-exp \u662f\u5df2\u9000\u5f79\u6a21\u578b\u7684\u517c\u5bb9\u522b\u540d\u3002\u5bb9\u91cf\uff1a1,048,576 \u4e0a\u4e0b\u6587 / \u6700\u5927\u8f93\u51fa 384K\uff08393,216\uff1b\u9ed8\u8ba4\u975e\u601d\u8003 8K\u3001\u601d\u8003 64K\u3001effort=max \u65f6 128K\uff09\u3002"
    },
    {
      "id": "deepseek-v3",
      "patterns": [
        "deepseek-v3",
        "deepseek-chat"
      ],
      "efforts": {
        "off": "none",
        "high": "high",
        "max": "max"
      },
      "compat": {
        "thinkingFormat": "deepseek",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "contextWindow": 163840,
      "maxTokens": 65536,
      "note": "DeepSeek V3 \u6863\u4f4d\uff1aOff / High / Max\u3002\u5b98\u65b9\u5df2\u505c\u552e V3 \u4ee3\uff08\u5b9a\u4ef7\u9875\u4ec5\u5269 V4 \u4e09\u578b\uff09\uff0c\u5bb9\u91cf\u53d6\u76ee\u5f55\u73b0\u5f79\u503c\u3002"
    },
    {
      "id": "deepseek-r1",
      "patterns": [
        "deepseek-r1",
        "deepseek-reasoner"
      ],
      "efforts": {
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "deepseek",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "contextWindow": 163840,
      "maxTokens": 32768,
      "note": "DeepSeek-R1 \u4e3a\u63a8\u7406\u6a21\u578b\uff0c\u4ec5\u63d0\u4f9b High\u3002\u5b98\u65b9\u5df2\u4e0b\u67b6 R1 \u4ee3\uff0c\u5bb9\u91cf\u53d6\u76ee\u5f55 r1-0528 \u503c\u3002"
    },
    {
      "id": "openai-gpt-5-2",
      "patterns": [
        "gpt-5.2"
      ],
      "efforts": {
        "off": "none",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "defaultEffort": "off",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 400000,
      "maxTokens": 128000,
      "note": "GPT-5.2 \u6863\u4f4d\uff1aNone / Low / Medium / High / XHigh\uff08\u9ed8\u8ba4 None\uff09\u3002\u5b98\u65b9\u53e6\u652f\u6301 PDF \u8f93\u5165\uff08\u6838\u5fc3\u8bcd\u8868\u6682\u4e0d\u542b\uff09\u3002gpt-5.2-pro \u5b98\u65b9\u9875\u672a\u5355\u5217\u6863\u4f4d\u884c\uff0c\u6309\u672c\u6761\u76ee\u540c\u6863\u5904\u7406\uff1bgpt-5.2-codex \u89c1\u5355\u72ec\u6761\u76ee\u3002"
    },
    {
      "id": "openai-gpt-5-2-codex",
      "patterns": [
        "gpt-5.2-codex"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "defaultEffort": "medium",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 400000,
      "maxTokens": 128000,
      "note": "GPT-5.2-Codex \u6863\u4f4d\uff1aLow / Medium / High / XHigh\uff08\u65e0 None \u6863\uff0c\u52ff\u52fe Off\uff09\uff0c\u5e26\u56fe\u8f93\u5165\u3001400K\u3002"
    },
    {
      "id": "openai-gpt-5-6",
      "patterns": [
        "gpt-5.6"
      ],
      "efforts": {
        "off": "none",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh",
        "max": "max"
      },
      "defaultEffort": "medium",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1050000,
      "maxTokens": 128000,
      "note": "GPT-5.6\uff08\u522b\u540d\u5373 sol\uff09\u6863\u4f4d\uff1aNone / Low / Medium(\u9ed8\u8ba4) / High / XHigh / Max\uff1bsol/luna/terra \u540c\u6863\uff0c\u5e26\u56fe\u8f93\u5165\u3002"
    },
    {
      "id": "openai-gpt-5-5",
      "patterns": [
        "gpt-5.5"
      ],
      "efforts": {
        "off": "none",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "defaultEffort": "medium",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1050000,
      "maxTokens": 128000,
      "note": "GPT-5.5 \u6863\u4f4d\uff1aNone / Low / Medium(\u9ed8\u8ba4) / High / XHigh\uff0c\u5e26\u56fe\u8f93\u5165\u3002pro \u53d8\u4f53\u4ec5 Medium / High(\u9ed8\u8ba4) / XHigh \u4e14\u4ec5 Responses API\u3002"
    },
    {
      "id": "openai-gpt-5-4",
      "patterns": [
        "gpt-5.4"
      ],
      "efforts": {
        "off": "none",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "defaultEffort": "off",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1050000,
      "maxTokens": 128000,
      "note": "GPT-5.4 \u6863\u4f4d\uff1aNone(\u9ed8\u8ba4) / Low / Medium / High / XHigh\uff0c\u5e26\u56fe\u8f93\u5165\u3002pro \u53d8\u4f53\u4ec5 Medium/High/XHigh\uff1bmini/nano \u4e3a 400K \u4e0a\u4e0b\u6587\u3002"
    },
    {
      "id": "openai-gpt-5-3",
      "patterns": [
        "gpt-5.3"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "defaultEffort": "medium",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 400000,
      "maxTokens": 128000,
      "note": "GPT-5.3-Codex \u6863\u4f4d\uff1aLow / Medium / High / XHigh\uff08\u65e0 None \u6863\uff09\uff0c\u5e26\u56fe\u8f93\u5165\u3001400K\uff1bgpt-5.3-chat \u4e3a\u975e\u63a8\u7406\u804a\u5929\u6a21\u578b\uff08\u89c1 chat \u6761\u76ee\uff09\u3002"
    },
    {
      "id": "openai-gpt-5-1",
      "patterns": [
        "gpt-5.1"
      ],
      "efforts": {
        "off": "none",
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "defaultEffort": "off",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 400000,
      "maxTokens": 128000,
      "note": "GPT-5.1 \u6863\u4f4d\uff1aNone / Low / Medium / High\uff08\u9ed8\u8ba4 None\uff09\u3002"
    },
    {
      "id": "openai-gpt-5-1-codex",
      "patterns": [
        "gpt-5.1-codex"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 400000,
      "maxTokens": 128000,
      "note": "GPT-5.1-Codex \u7cfb\u5217\uff1a\u5b98\u65b9\u6a21\u578b\u9875\u672a\u5355\u5217 effort \u503c\u57df\uff0c\u6309\u540c\u4ee3\u4fdd\u5b88\u6863 Low / Medium / High\uff08\u65e0 None\uff1bxhigh \u672a\u8bc1\u5b9e\uff09\u3002\u5982\u7aef\u70b9\u652f\u6301 xhigh/none \u53ef\u624b\u8c03\u3002"
    },
    {
      "id": "openai-gpt-5",
      "patterns": [
        "gpt-5"
      ],
      "efforts": {
        "minimal": "minimal",
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "defaultEffort": "medium",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 400000,
      "maxTokens": 128000,
      "note": "GPT-5 \u521d\u4ee3\u6863\u4f4d\uff1aMinimal / Low / Medium / High\uff0c\u65e0\u5173\u95ed\u6863\u3002"
    },
    {
      "id": "openai-chat",
      "patterns": [
        "gpt-5.1-chat-latest",
        "gpt-5.2-chat-latest",
        "gpt-5.3-chat-latest",
        "gpt-5-chat-latest",
        "gpt-chat-latest",
        "gpt-5-chat",
        "gpt-5.1-chat",
        "gpt-5.2-chat",
        "gpt-5.3-chat"
      ],
      "efforts": false,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 128000,
      "maxTokens": 16384,
      "note": "-chat \u7cfb\u5217\uff08\u5b98\u65b9 id \u4e3a gpt-5.x-chat-latest\uff09\u4e3a\u975e\u63a8\u7406\u804a\u5929\u6a21\u578b\uff0c\u4e0d\u652f\u6301 effort \u53c2\u6570\uff08\u52ff\u52fe\u601d\u8003\u6863\uff09\uff1b\u5b98\u65b9\u652f\u6301\u56fe\u7247\u8f93\u5165\uff0c128K / 16,384 \u8f93\u51fa\u3002gpt-5-chat-latest \u5df2\u4e8e 2026-07-23 \u4e0b\u67b6\u3001gpt-chat-latest \u5df2\u65e0\u5b98\u65b9\u9875\u9762\uff08\u4fdd\u7559\u6a21\u5f0f\u4f9b\u7f51\u5173\uff09\u3002"
    },
    {
      "id": "openai-o",
      "patterns": [
        "o1",
        "o3",
        "o4"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "defaultEffort": "medium",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 200000,
      "maxTokens": 100000,
      "note": "OpenAI o \u7cfb\u6863\u4f4d\uff1aLow / Medium / High\u3002\u5b98\u65b9\u5df2\u4e8e 2026-06 \u516c\u544a\u9000\u5f79\uff08o1/o1-pro/o3-mini/o4-mini 2026-10-23 \u79fb\u9664\u3001o3/o3-pro 2026-12-11\uff09\uff0c\u7f51\u5173\u6b8b\u7559\u4ecd\u53ef\u547d\u4e2d\uff1b\u591a\u6570 o \u7cfb\u7aef\u70b9\u6536\u56fe\uff08o3-mini \u4f8b\u5916\uff09\u3002"
    },
    {
      "id": "openai-gpt-oss",
      "patterns": [
        "gpt-oss"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "defaultEffort": "low",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "contextWindow": 131072,
      "maxTokens": 131072,
      "note": "GPT-OSS \u5f00\u6e90\u6743\u91cd\uff08Ollama/vLLM \u5e38\u89c1\uff09\uff1areasoning effort Low / Medium / High\uff0c\u7eaf\u6587\u672c\uff0c131K \u4e0a\u4e0b\u6587 / 131K \u8f93\u51fa\u30022026-09 \u590d\u6838\uff1a\u5b98\u65b9\u6a21\u578b\u9875\u73b0\u5728\u5199 Chat Completions = Not supported\u3001\u65e0\u56fe\u7247\u8f93\u5165\uff08\u9ed8\u8ba4 Low \u6765\u81ea\u5b98\u65b9 CLI\uff0c\u4e0d\u662f API \u9875\uff09\uff0c\u56e0\u6b64\u8fd9\u91cc\u4e0d\u518d\u58f0\u660e Off\u3002"
    },
    {
      "id": "openai-gpt-6-astra",
      "patterns": [
        "gpt-6-astra",
        "gpt-6"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh",
        "max": "max"
      },
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1050000,
      "maxTokens": 128000,
      "note": "GPT-6 Astra \u6863\u4f4d\uff1aLow / Medium / High / XHigh / Max\u2014\u2014**\u6ca1\u6709 None \u6863**\uff08\u5b98\u65b9\u539f\u6587\uff1a\u8bbe\u4e3a none \u8fd4\u56de HTTP 400\uff09\uff0c\u56e0\u6b64\u672c\u6761\u76ee\u4e0d\u58f0\u660e Off\u3002\u5e26\u56fe\u8f93\u5165\uff0c1,050,000 \u4e0a\u4e0b\u6587 / 128,000 \u8f93\u51fa\uff1bAI \u5b98\u65b9\u9ed8\u8ba4\u6863\u4f4d\u672a\u516c\u5e03\uff0c\u6545\u4e0d\u586b\u3002\u5de5\u5177\u8c03\u7528\u9700\u8d70 Responses API\u3002"
    },
    {
      "id": "openai-gpt-5-6-cyber",
      "patterns": [
        "gpt-5.6-cyber"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 400000,
      "maxTokens": 128000,
      "note": "GPT-5.6-Cyber\uff1a\u5b98\u65b9\u6a21\u578b\u9875\u672a\u5355\u5217 effort \u503c\u57df\uff08\u4e0d\u7b49\u4e8e\u4e0d\u652f\u6301\uff09\uff0c\u6545\u6309\u540c\u4ee3\u4fdd\u5b88\u6863 Low / Medium / High / XHigh\uff1b\u8be5\u578b\u53f7\u4ec5 Responses API\uff0c\u5e26\u56fe\u8f93\u5165\u3001400K \u4e0a\u4e0b\u6587\u3002\u5b98\u65b9\u652f\u6301\u7684\u5176\u4ed6\u6863\u4f4d\u53ef\u624b\u8c03\u540e\u5e94\u7528\u3002"
    },
    {
      "id": "openai-gpt-4o",
      "patterns": [
        "gpt-4o"
      ],
      "efforts": false,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 128000,
      "maxTokens": 16384,
      "note": "GPT-4o \u4ee3\u9645\uff1a\u975e\u63a8\u7406\u6a21\u578b\uff0c\u4e0d\u652f\u6301 effort \u53c2\u6570\uff08\u52ff\u52fe\u601d\u8003\u6863\uff09\uff1b\u56fe\u7247\u8f93\u5165\u5168\u7cfb\u6807\u914d\uff0c128K / 16,384 \u8f93\u51fa\u3002"
    },
    {
      "id": "openai-gpt-4-1",
      "patterns": [
        "gpt-4.1"
      ],
      "efforts": false,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1047576,
      "maxTokens": 32768,
      "note": "GPT-4.1 \u5168\u7cfb\uff08\u542b mini/nano\uff09\uff1a\u975e\u63a8\u7406\u6a21\u578b\uff0c\u4e0d\u652f\u6301 effort \u53c2\u6570\uff1b\u5b98\u65b9 1,047,576 \u4e0a\u4e0b\u6587 / 32,768 \u8f93\u51fa\uff0c\u5168\u7cfb\u5e26\u56fe\u8f93\u5165\u3002"
    },
    {
      "id": "openai-gpt-4-turbo-preview",
      "patterns": [
        "gpt-4-turbo-preview"
      ],
      "efforts": false,
      "input": [
        "text"
      ],
      "contextWindow": 128000,
      "maxTokens": 4096,
      "note": "GPT-4 Turbo Preview\uff1a\u975e\u63a8\u7406\u6a21\u578b\uff0c\u7eaf\u6587\u672c\u8f93\u5165\uff08\u6b63\u5f0f turbo \u5feb\u7167\u652f\u6301\u56fe\u7247\uff0c\u89c1\u4e0b\u6761\uff09\uff0c128K\u3002"
    },
    {
      "id": "openai-gpt-4-turbo",
      "patterns": [
        "gpt-4-turbo"
      ],
      "efforts": false,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 128000,
      "maxTokens": 4096,
      "note": "GPT-4 Turbo\uff1a\u975e\u63a8\u7406\u6a21\u578b\uff0c\u5b98\u65b9\u652f\u6301\u56fe\u7247\u8f93\u5165\uff0c128K / 4,096 \u8f93\u51fa\u3002"
    },
    {
      "id": "openai-gpt",
      "patterns": [
        "gpt-4",
        "gpt-3.5"
      ],
      "efforts": false,
      "input": [
        "text"
      ],
      "note": "GPT-4/3.5 \u4ee3\u9645\uff1a\u975e\u63a8\u7406\u6a21\u578b\uff0c\u4e0d\u652f\u6301 effort \u53c2\u6570\uff08\u52ff\u52fe\u601d\u8003\u6863\uff09\u3002gpt-4-turbo/4.1 \u8d77\u652f\u6301\u56fe\u7247\uff0c\u89c1\u5355\u72ec\u6761\u76ee\uff1b\u65b0\u4ee3\u8bf7\u7528 GPT-5 \u7cfb\uff08\u89c1 openai-chat/gpt-5.x \u6761\u76ee\uff09\u3002"
    },
    {
      "id": "anthropic-claude-5",
      "patterns": [
        "claude-fable-5",
        "claude-mythos-5",
        "claude-opus-5",
        "claude-sonnet-5"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh",
        "max": "max"
      },
      "defaultEffort": "high",
      "compat": {
        "supportsReasoningEffort": true
      },
      "anthropicAdaptive": true,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1000000,
      "maxTokens": 128000,
      "note": "Claude 5 \u4ee3\uff08Fable 5 / Mythos 5 / Opus 5 / Sonnet 5\uff09\u6863\u4f4d\uff1aLow / Medium / High(\u9ed8\u8ba4) / XHigh / Max\uff1bFable 5.1 \u4e0e Mythos 5.1 \u89c1\u5355\u72ec\u6761\u76ee\uff0cMythos Preview \u4ec5\u81f3 Max\u30021M \u4e0a\u4e0b\u6587 / 128K \u8f93\u51fa\uff08Batch 300K\uff09\u3002\u5b98\u65b9\u652f\u6301 PDF \u8f93\u5165\u3002\u6ce8\u610f\uff1aAnthropic \u5b98\u65b9 OpenAI \u517c\u5bb9\u5c42\u4f1a\u5ffd\u7565 effort \u53c2\u6570\uff0c\u58f0\u660e\u5728\u7b2c\u4e09\u65b9\u7f51\u5173\u6620\u5c04\u65f6\u751f\u6548\u3002"
    },
    {
      "id": "anthropic-claude-5-1",
      "patterns": [
        "claude-fable-5-1",
        "claude-mythos-5-1"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh",
        "max": "max"
      },
      "defaultEffort": "high",
      "compat": {
        "supportsReasoningEffort": true
      },
      "anthropicAdaptive": true,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1000000,
      "maxTokens": 128000,
      "note": "Claude Fable 5.1 / Mythos 5.1\uff1a\u5b98\u65b9\u6863\u4f4d Low / Medium / High(\u9ed8\u8ba4) / XHigh / Max\uff0c\u81ea\u9002\u5e94\u601d\u8003\u5e38\u5f00\uff08\u4e0d\u63a5\u53d7 enabled/disabled\uff09\u30021M \u4e0a\u4e0b\u6587 / 128K \u8f93\u51fa\uff1b\u8fd9\u4e24\u578b\u4e5f\u662f\u5b98\u65b9\u552f\u4e00\u5141\u8bb8\u4f1a\u8bdd\u4e2d\u9014\u6539\u6863\u7684\uff08\u9700 beta header\uff0c\u672c\u63d2\u4ef6\u4e0d\u6d89\u53ca\uff09\u3002"
    },
    {
      "id": "anthropic-claude-mythos-preview",
      "patterns": [
        "claude-mythos-preview"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "max": "max"
      },
      "defaultEffort": "high",
      "compat": {
        "supportsReasoningEffort": true
      },
      "anthropicAdaptive": true,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1000000,
      "maxTokens": 128000,
      "note": "Claude Mythos Preview\uff1a\u5b98\u65b9\u6863\u4f4d Low / Medium / High / Max\uff08\u65e0 XHigh\uff09\uff0c1M \u4e0a\u4e0b\u6587\u3002"
    },
    {
      "id": "anthropic-claude-opus-4-high",
      "patterns": [
        "claude-opus-4-8",
        "claude-opus-4-7"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh",
        "max": "max"
      },
      "defaultEffort": "high",
      "compat": {
        "supportsReasoningEffort": true
      },
      "anthropicAdaptive": true,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1000000,
      "maxTokens": 128000,
      "note": "Claude Opus 4.7/4.8 \u6863\u4f4d\uff1aLow / Medium / High(\u9ed8\u8ba4) / XHigh / Max\uff1bxhigh \u4e3a\u5b98\u65b9\u63a8\u8350\u7684\u7f16\u7801\u8d77\u6b65\u6863\u30021M \u4e0a\u4e0b\u6587\u3002"
    },
    {
      "id": "anthropic-claude-4-6",
      "patterns": [
        "claude-opus-4-6",
        "claude-sonnet-4-6"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "max": "max"
      },
      "defaultEffort": "high",
      "compat": {
        "supportsReasoningEffort": true
      },
      "anthropicAdaptive": true,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1000000,
      "maxTokens": 128000,
      "note": "Claude 4.6 \u4ee3\u6863\u4f4d\uff1aLow / Medium / High / Max\uff08\u65e0 XHigh\u2014\u2014\u5b98\u65b9\u660e\u8a00\u300c\u652f\u6301 max \u7684\u90e8\u5206\u578b\u53f7\u4e0d\u652f\u6301 xhigh\u300d\uff09\u30021M \u4e0a\u4e0b\u6587\u3002"
    },
    {
      "id": "anthropic-claude-opus-4-5",
      "patterns": [
        "claude-opus-4-5"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 200000,
      "maxTokens": 64000,
      "note": "Claude Opus 4.5\uff1a\u5b98\u65b9 effort \u652f\u6301\u5217\u8868\uff0820251101 \u5feb\u7167\uff09\uff0c\u6863\u4f4d Low / Medium / High\uff08\u65e0 XHigh/Max\uff09\uff0c\u53ef\u4e0e budget_tokens \u5e76\u7528\uff1b200K / 64K\u3002"
    },
    {
      "id": "anthropic-claude",
      "patterns": [
        "claude"
      ],
      "efforts": false,
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 200000,
      "maxTokens": 64000,
      "note": "Claude 3.x \u4e0e Sonnet 4.5 / Haiku 4.5\uff1a\u5b98\u65b9 effort \u53c2\u6570\u4e0d\u652f\u6301\uff08\u4ec5 Fable/Mythos 5\u3001Opus 5/4.6-4.8\u3001Sonnet 5/4.6\u3001Opus 4.5 \u652f\u6301\uff09\uff0c\u601d\u8003\u7531 thinking.type \u63a7\u5236\u2014\u2014\u52ff\u52fe\u601d\u8003\u6863\u3002\u53c2\u8003\u5bb9\u91cf 200K / 64K\uff08Haiku 3.5 \u4e3a\u7eaf\u6587\u672c\uff0c\u6309\u9700\u53d6\u6d88\u56fe\u7247\uff09\u3002"
    },
    {
      "id": "google-gemini",
      "patterns": [
        "gemini"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1048576,
      "maxTokens": 65536,
      "note": "Gemini \u901a\u7528\u5b89\u5168\u6863\uff1aLow / Medium / High\uff08\u5b98\u65b9 OpenAI \u517c\u5bb9\u6620\u5c04\u8868\u53e6\u6536 minimal\uff1a2.5 \u7cfb\u6620\u5c04\u4e3a 1,024 \u9884\u7b97\u30013.1 Flash-Lite/3 Flash \u539f\u751f minimal\u30013.1 Pro \u843d low\uff09\u3002none \u4ec5\u80fd\u5173 2.5 \u975e Pro\uff1b2.5 Pro \u4e0e 3 \u4ee3\u4e0d\u53ef\u5173\uff1b\u5404\u578b\u9ed8\u8ba4\u4e0d\u4e00\uff08flash-lite \u9ed8\u8ba4\u5173\uff09\u3002\u5b98\u65b9\u53e6\u6536\u97f3\u9891/\u89c6\u9891/PDF\u3002"
    },
    {
      "id": "xai-grok-high",
      "patterns": [
        "grok-4.6"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 500000,
      "note": "Grok 4.6 \u6863\u4f4d\uff1aLow / Medium / High(\u9ed8\u8ba4) / XHigh\uff0c\u601d\u8003\u4e0d\u53ef\u5173\u95ed\uff1b\u5e26\u56fe\u8f93\u5165\u3001500K \u4e0a\u4e0b\u6587\u3002grok-4.7 \u4e0d\u5b58\u5728\uff08\u5b98\u65b9 404 \u5df2\u6838\uff09\uff0c\u5df2\u9664\u540d\u3002"
    },
    {
      "id": "xai-grok-4-5",
      "patterns": [
        "grok-4.5"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 500000,
      "note": "Grok 4.5 \u6863\u4f4d\uff1aLow / Medium / High(\u9ed8\u8ba4)\uff0c\u601d\u8003\u4e0d\u53ef\u5173\u95ed\uff1b\u5e26\u56fe\u8f93\u5165\u3002\u4f20\u5165 xhigh \u4f1a\u88ab\u5b98\u65b9\u9759\u9ed8\u6309 High \u5904\u7406\u3002"
    },
    {
      "id": "xai-grok-4-3",
      "patterns": [
        "grok-4.3"
      ],
      "efforts": {
        "off": "none",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "defaultEffort": "low",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1000000,
      "note": "Grok 4.3\uff1a\u5b98\u65b9\u56db\u7ea7 reasoning effort\uff08None / Low / Medium / High\uff09\uff0c1M \u4e0a\u4e0b\u6587\u3001\u5e26\u56fe\u8f93\u5165\uff1bgrok-4-fast \u7b49\u65e7 slug 2026-05-15 \u8d77\u81ea\u52a8\u91cd\u5b9a\u5411\u5230\u672c\u578b\u53f7\u3002"
    },
    {
      "id": "xai-grok",
      "patterns": [
        "grok"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "note": "Grok \u901a\u7528\u6863\u4f4d\uff1aLow / Medium / High\u3002\u521d\u4ee3 grok-4\u3001grok-4.20 \u4e0e grok-build-0.1 \u4e0d\u63a5\u53d7\u8be5\u53c2\u6570\uff08grok-4 \u7cfb\u4e0e grok-3 \u5df2\u4e8e 2026-05-15 \u9000\u5f79\u5e76\u91cd\u5b9a\u5411\u81f3 4.3\uff09\uff1bgrok-4.20-multi-agent \u7684\u56db\u6863\u63a7\u5236\u7684\u662f agent \u6570\u91cf\u800c\u975e\u601d\u8003\u6df1\u5ea6\u3002\u65b0\u65e7\u4ee3\u9645\u8bf7\u4f18\u5148\u9009 4.5/4.6/4.3\uff1b\u591a\u6a21\u6001\u53d8\u4f53\u6309\u9700\u52fe\u9009\u56fe\u7247\u3002"
    },
    {
      "id": "mistral-magistral",
      "patterns": [
        "magistral"
      ],
      "efforts": false,
      "input": [
        "text"
      ],
      "contextWindow": 32768,
      "maxTokens": 32768,
      "note": "Magistral \u539f\u751f\u601d\u8003\u7ebf\uff08\u65e0 effort \u53c2\u6570\uff0c\u4e3a prompt_mode \u8bed\u4e49\uff09\uff0c\u5b98\u65b9\u5df2\u4e8e 2026-07-28 \u58f0\u660e\u5f03\u7528\u3001\u9010\u6b65\u64a4\u51fa\uff1b\u73b0\u5f79\u63a8\u7406\u8d70 mistral-small-2603 / mistral-medium-3-5 \u7684 reasoning_effort\uff08\u89c1\u4e0b\u6761\uff09\u3002"
    },
    {
      "id": "mistral-medium-3",
      "patterns": [
        "mistral-medium-3.5",
        "mistral-small-latest",
        "mistral-small-2603"
      ],
      "efforts": {
        "off": "none",
        "high": "high"
      },
      "defaultEffort": "off",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "note": "Mistral \u73b0\u5f79\u63a8\u7406\u6863\uff1aNone / High\u2014\u2014\u5b98\u65b9 reasoning_effort \u679a\u4e3e\uff08mistral-common \u534f\u8bae\u5e93\uff09\u5373 none/high\uff1bmistral-small-2603\uff08Small 4\uff09\u4e0e mistral-medium-3-5 \u7ecf\u5b83\u63a7\u5236\uff0cMedium 3.5 \u5e26\u89c6\u89c9\u3002\u5bb9\u91cf\u672a\u5728\u5b98\u65b9\u76ee\u5f55\u9875\u5355\u5217\uff0c\u4e0d\u63d0\u4f9b\u3002"
    },
    {
      "id": "qwen-vision",
      "patterns": [
        "qwen-vl",
        "qwen2-vl",
        "qwen2-5-vl",
        "qwen3-vl",
        "qvq"
      ],
      "efforts": {
        "off": null,
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "qwen"
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 131072,
      "maxTokens": 8192,
      "note": "\u901a\u4e49\u89c6\u89c9\u7ebf\uff08Qwen-VL/QvQ\uff09\uff1aenable_thinking \u5f00\u5173\uff08\u5f00=High\uff09\uff0c\u6536\u56fe\u3002qwen3-vl \u5bb9\u91cf\u66f4\u5927\uff0c\u6309\u9700\u4e0a\u8c03\u3002"
    },
    {
      "id": "qwen-3-8",
      "patterns": [
        "qwen3.8"
      ],
      "efforts": {
        "off": null,
        "low": "low",
        "medium": "medium",
        "xhigh": "xhigh"
      },
      "defaultEffort": "xhigh",
      "compat": {
        "thinkingFormat": "qwen",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1000000,
      "note": "Qwen 3.8 \u7cfb\uff1a\u5b98\u65b9 reasoning_effort \u6863\u4f4d XHigh(\u9ed8\u8ba4) / Medium / Low\uff0cthinking \u9ed8\u8ba4\u5f00\u3001\u53ef\u6309\u8bf7\u6c42\u5173\u95ed\uff1b\u539f\u751f\u591a\u6a21\u6001\uff08qwen3.8-max \u56fe\u50cf/\u89c6\u9891\u7406\u89e3\uff0c\u89c6\u9891\u672a\u5165\u6838\u5fc3\u8bcd\u8868\uff09\u30021M \u6863\u4e0a\u4e0b\u6587\u300227B \u4e0e Flash-Next \u5f00\u6e90\u6b3e\u89c1\u5355\u72ec\u6761\u76ee\u3002"
    },
    {
      "id": "qwen-3-8-27b",
      "patterns": [
        "qwen3.8-27b"
      ],
      "efforts": {
        "off": null,
        "low": "low",
        "medium": "medium",
        "xhigh": "xhigh"
      },
      "defaultEffort": "xhigh",
      "compat": {
        "thinkingFormat": "qwen",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 262144,
      "note": "Qwen3.8-27B\uff08dense\uff0c2026-08-14 \u5f00\u6e90\uff09\uff1a\u5b98\u65b9 reasoning_effort \u6863\u4f4d XHigh(\u9ed8\u8ba4) / Medium / Low\uff0cthinking \u9ed8\u8ba4\u5f00\u3001\u53ef\u6309\u8bf7\u6c42\u5173\uff1b\u539f\u751f\u56fe\u50cf+\u89c6\u9891\u7406\u89e3\uff08\u89c6\u9891\u672a\u5165\u6838\u5fc3\u8bcd\u8868\uff09\u3002262,144 \u539f\u751f\u4e0a\u4e0b\u6587\u3001\u5b98\u65b9\u58f0\u660e\u53ef\u6269\u81f3 1M\u3002\u6765\u6e90\uff1aHF Qwen/Qwen3.8-27B \u6a21\u578b\u5361\u3002"
    },
    {
      "id": "qwen-3-8-flash-next",
      "patterns": [
        "qwen3.8-flash-next"
      ],
      "efforts": {
        "off": null,
        "low": "low",
        "medium": "medium",
        "xhigh": "xhigh"
      },
      "defaultEffort": "xhigh",
      "compat": {
        "thinkingFormat": "qwen",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 262144,
      "note": "Qwen3.8-Flash-Next\uff08125B-A6B \u5b9e\u9a8c\u67b6\u6784\uff0cQwen4 \u524d\u8eab\uff09\uff1a\u5b98\u65b9 reasoning_effort \u6863\u4f4d XHigh(\u9ed8\u8ba4) / Medium / Low + enable_thinking \u5f00\u5173\uff1b\u539f\u751f\u89c6\u89c9\uff08Vision Encoder\uff09\u3002262,144 \u539f\u751f\u4e0a\u4e0b\u6587\u3001\u53ef\u6269\u81f3 1M\u3002\u6765\u6e90\uff1aHF \u6a21\u578b\u5361\u4e0e qwen.ai \u5b98\u65b9\u535a\u5ba2\u3002"
    },
    {
      "id": "qwen",
      "patterns": [
        "qwen",
        "qwq"
      ],
      "efforts": {
        "off": null,
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "qwen"
      },
      "input": [
        "text"
      ],
      "contextWindow": 1000000,
      "maxTokens": 65536,
      "note": "\u901a\u4e49\u5343\u95ee\uff1aenable_thinking \u5f00\u5173\uff08\u65e0 effort \u6863\uff09\uff0c\u5f00=High\uff1b\u73b0\u5f79\u65d7\u8230\u4e3a qwen3.8 \u7cfb\uff081M \u6863\u4e0a\u4e0b\u6587\uff0c\u89c1 qwen-3-8 \u6761\u76ee\uff09\u30023.6/3.7 \u4ee3\u7684 Plus/Flash \u4ea6\u9ed8\u8ba4\u591a\u6a21\u6001\uff08\u56fe\u7247/\u89c6\u9891\uff09\uff0c\u5982\u63a5\u5165\u8bf7\u6309\u9700\u52fe\u9009\u56fe\u7247\uff1b\u89c6\u89c9\u7ebf\u89c1 qwen-vision \u6761\u76ee\u3002"
    },
    {
      "id": "glm-vision",
      "patterns": [
        "glm-4v",
        "glm-4-6v",
        "glm-4-5v",
        "glm-5v"
      ],
      "efforts": {
        "off": null,
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "zai"
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 131072,
      "maxTokens": 32768,
      "note": "\u667a\u8c31\u89c6\u89c9\u7ebf\uff08GLM-4V/4.5V/4.6V/5V\uff09\uff1athinking \u5f00\u5173\uff08\u5f00=High\uff09\uff0c\u6536\u56fe\u3002GLM-4.5V \u4e3a\u5f3a\u5236\u601d\u8003\uff08\u4f20 disabled \u62a5\u9519\uff0c\u8bf7\u624b\u52a8\u5220 Off \u6863\uff09\u3002"
    },
    {
      "id": "glm-5-3-flash",
      "patterns": [
        "glm-5.3-flash"
      ],
      "efforts": {
        "low": "low",
        "high": "high",
        "max": "max"
      },
      "defaultEffort": "max",
      "compat": {
        "thinkingFormat": "zai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1048576,
      "maxTokens": 131072,
      "note": "GLM-5.3-Flash\uff08320B\uff0c\u5b98\u65b9\u6587\u6863 vlm \u5206\u7c7b\uff09\uff1a\u5f3a\u5236\u601d\u8003\uff08thinking.type \u4ec5 enabled\uff0c\u4e0d\u652f\u6301\u5173\u95ed\uff09\uff0c\u6587\u672c\u53c2\u6570\u4e0e GLM-5.3 \u4e00\u81f4\u2014\u2014\u6863\u4f4d Low / High / Max\u3002\u8f93\u5165\u6a21\u6001\uff1a\u89c6\u9891\u3001\u56fe\u50cf\u3001\u6587\u672c\u3001\u6587\u4ef6\uff08\u89c6\u9891/\u6587\u4ef6\u672a\u5165\u6838\u5fc3\u8bcd\u8868\uff0c\u56fe\u7247\u53ef\u52fe\uff09\u3002\u5b98\u65b9 1M \u4e0a\u4e0b\u6587 / 128K \u6700\u5927\u8f93\u51fa\u3002\u6765\u6e90\uff1adocs.bigmodel.cn \u6a21\u578b\u9875\u3002"
    },
    {
      "id": "glm-5-3",
      "patterns": [
        "glm-5.3"
      ],
      "efforts": {
        "low": "low",
        "high": "high",
        "max": "max"
      },
      "defaultEffort": "max",
      "compat": {
        "thinkingFormat": "zai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "contextWindow": 1048576,
      "maxTokens": 131072,
      "note": "GLM-5.3 \u6863\u4f4d\uff1aLow / High / Max\uff08\u5f3a\u5236\u601d\u8003\uff0c\u5176\u4f59\u503c\u62a5\u9519\uff09\u3002\u5b98\u65b9\u5bb9\u91cf 1M / 128K\u3002"
    },
    {
      "id": "glm-5-2",
      "patterns": [
        "glm-5.2"
      ],
      "efforts": {
        "off": "none",
        "minimal": "minimal",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh",
        "max": "max"
      },
      "defaultEffort": "max",
      "compat": {
        "thinkingFormat": "zai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "contextWindow": 1048576,
      "maxTokens": 131072,
      "note": "GLM-5.2 \u6863\u4f4d\uff1aNone / Minimal / Low / Medium / High / XHigh / Max\uff08\u5b98\u65b9\u6620\u5c04\uff1aLow\u00b7Medium\u2192High\u3001XHigh\u2192Max\u3001None\u00b7Minimal=\u505c\u6b62\u601d\u8003\uff09\u3002\u89c6\u89c9\u7ebf\u89c1 glm-vision \u6761\u76ee\u3002"
    },
    {
      "id": "glm",
      "patterns": [
        "glm",
        "zhipu",
        "chatglm"
      ],
      "efforts": {
        "off": null,
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "zai"
      },
      "input": [
        "text"
      ],
      "note": "GLM \u901a\u7528\uff1athinking \u5f00\u5173\uff08\u65e0 effort \u6863\uff09\uff0c\u5f00=High\uff1beffort \u9636\u68af\u4ec5 GLM-5.2+ \u652f\u6301\uff08\u89c1\u4e0a\u4e24\u6761\u76ee\uff09\u3002\u6ce8\u610f GLM-4.7/GLM-4.5V \u4e3a\u5f3a\u5236\u601d\u8003\uff0c\u4f20 disabled \u4f1a\u62a5\u9519\uff08\u8bf7\u624b\u52a8\u5220 Off \u6863\uff09\u3002\u89c6\u89c9\u7ebf\u89c1 glm-vision \u6761\u76ee\u3002"
    },
    {
      "id": "kimi-k3",
      "patterns": [
        "kimi-k3"
      ],
      "efforts": {
        "low": "low",
        "high": "high",
        "max": "max"
      },
      "defaultEffort": "max",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1048576,
      "note": "Kimi K3 \u6863\u4f4d\uff1aLow / High / Max(\u9ed8\u8ba4 Max)\uff0c\u8d70\u9876\u5c42 reasoning_effort\uff1b\u59cb\u7ec8\u63a8\u7406\u3001\u52ff\u4f20 thinking \u5bf9\u8c61\u3002\u539f\u751f\u89c6\u89c9\u7406\u89e3\uff0c1M \u4e0a\u4e0b\u6587\uff08\u6700\u5927\u8f93\u51fa\u5b98\u65b9\u672a\u5355\u72ec\u5217\uff0c\u4e0d\u63d0\u4f9b\uff09\u3002"
    },
    {
      "id": "kimi-k2-vision",
      "patterns": [
        "kimi-k2.6",
        "kimi-k2.5"
      ],
      "efforts": {
        "off": null,
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "deepseek"
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 262144,
      "note": "Kimi K2.5/K2.6 \u89c6\u89c9\u4ee3\uff1athinking.type \u5f00\u5173\uff08\u9ed8\u8ba4\u5f00\u3001\u53ef\u5173\uff09\uff0c\u5f00=High\uff1b\u5e26\u89c6\u89c9\uff0c256K\u3002K2.7 Code \u59cb\u7ec8\u601d\u8003\uff0c\u89c1\u5355\u72ec\u6761\u76ee\u3002"
    },
    {
      "id": "kimi-k27-code",
      "patterns": [
        "kimi-k2.7"
      ],
      "efforts": {
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "deepseek"
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 262144,
      "note": "Kimi K2.7 Code\uff08\u542b\u9ad8\u901f\u7248\uff09\uff1a\u59cb\u7ec8\u601d\u8003\u2014\u2014thinking.type \u4ec5\u63a5\u53d7 enabled\uff08\u4f20 disabled \u62a5\u9519\uff09\uff0c\u65e0 Off \u6863\uff1b\u5e26\u89c6\u89c9\uff0c256K\u3002"
    },
    {
      "id": "kimi-moonshot-v1-vision",
      "patterns": [
        "moonshot-v1-8k-vision",
        "moonshot-v1-32k-vision",
        "moonshot-v1-128k-vision"
      ],
      "efforts": false,
      "input": [
        "text",
        "image"
      ],
      "note": "Moonshot V1 \u89c6\u89c9\u65e7\u4ee3\uff088k/32k/128k \u5404\u4e00\uff09\uff1a\u65e0\u601d\u8003\u63a7\u4ef6\uff08\u751f\u6210\u6a21\u578b\uff09\u3001\u652f\u6301\u56fe\u7247\u8f93\u5165\uff1b\u8be5\u7ebf\u5df2\u505c\u6b62\u5bf9\u65b0\u7528\u6237\u5f00\u653e\uff082026-08-31 \u5168\u91cf\u4e0b\u7ebf\uff0c\u7f51\u5173\u6b8b\u7559\u4ecd\u53ef\u547d\u4e2d\uff09\u3002"
    },
    {
      "id": "kimi",
      "patterns": [
        "kimi",
        "moonshot"
      ],
      "efforts": {
        "off": null,
        "high": "high"
      },
      "compat": {
        "thinkingFormat": "deepseek"
      },
      "input": [
        "text"
      ],
      "contextWindow": 262144,
      "note": "Kimi \u901a\u7528\uff1athinking \u5f00\u5173\uff08\u65e0 effort \u6863\uff09\uff0c\u5f00=High\u3002k2 \u7cfb\u5217 2026-05-25 \u4e0b\u7ebf\u3001kimi-latest 2026-01-28 \u4e0b\u7ebf\u3001moonshot-v1 \u7cfb 2026-08-31 \u5168\u91cf\u4e0b\u7ebf\uff08\u7f51\u5173\u6b8b\u7559\u4ecd\u53ef\u547d\u4e2d\uff1bmoonshot-v1 \u672c\u8eab\u975e\u601d\u8003\u6a21\u578b\uff09\u3002\u89c6\u89c9\u4ee3\u4e0e K2.7 Code \u89c1\u5355\u72ec\u6761\u76ee\u3002"
    },
    {
      "id": "hunyuan-hy3",
      "patterns": [
        "hy3"
      ],
      "efforts": {
        "low": "low",
        "high": "high"
      },
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "contextWindow": 262144,
      "note": "\u6df7\u5143 hy3\uff1a\u5f00\u6e90\u5951\u7ea6\u7ecf chat_template_kwargs.reasoning_effort = no_think(\u9ed8\u8ba4)/low/high\uff1b\u5b98\u65b9\u6a21\u578b\u5361 256K \u4e0a\u4e0b\u6587\uff08295B MoE\uff0c2026 \u5f00\u6e90\uff09\u3002"
    },
    {
      "id": "hunyuan-hy4",
      "patterns": [
        "hy4-preview",
        "hy-4-preview"
      ],
      "efforts": {
        "off": "no_think",
        "high": "high"
      },
      "defaultEffort": "high",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "contextWindow": 1000000,
      "note": "\u6df7\u5143 Hy4 preview\uff1a\u5b98\u65b9 README\u2014\u2014reasoning \u9ed8\u8ba4 high\uff08\u6df1\u5ea6\u601d\u8003\uff09\uff0c\u5173\u95ed\u7ecf chat_template_kwargs.reasoning_effort=no_think\uff1b\u5b98\u65b9\u89c4\u683c\u8868 1M \u4e0a\u4e0b\u6587\uff08770B-A49B MoE\uff0cGated DSA\uff09\u3002low \u6863\u5b98\u65b9\u672a\u5217\uff0c\u5982\u6709\u8bf7\u624b\u8c03\uff1b\u89c6\u89c9\u672a\u58f0\u660e\uff0c\u6309\u9700\u624b\u52fe\u3002\u6765\u6e90\uff1aTencent-Hunyuan/Hy4-preview \u5b98\u65b9 README\u3002"
    },
    {
      "id": "step-3-7",
      "patterns": [
        "step-3.7",
        "step-3.6"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "defaultEffort": "medium",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 262144,
      "note": "\u9636\u8dc3 Step-3.6/3.7 \u6863\u4f4d\uff1aLow / Medium(\u9ed8\u8ba4\u63a8\u8350) / High\uff0c\u539f\u751f\u56fe\u7247+\u89c6\u9891\u7406\u89e3\u3002\u4e0a\u4e0b\u6587\u4e3a\u8f93\u5165+\u8f93\u51fa\u603b\u548c\u4e0a\u9650\u3002"
    },
    {
      "id": "step-3-5",
      "patterns": [
        "step-3.5"
      ],
      "efforts": {
        "low": "low",
        "high": "high"
      },
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "contextWindow": 262144,
      "note": "\u9636\u8dc3 Step-3.5 Flash \u6863\u4f4d\uff1aLow / High\uff08\u7eaf\u6587\u672c\u63a8\u7406\u65d7\u8230\uff09\u3002\u4e0a\u4e0b\u6587\u4e3a\u8f93\u5165+\u8f93\u51fa\u603b\u548c\u4e0a\u9650\u3002"
    },
    {
      "id": "step",
      "patterns": [
        "step-3",
        "step-2"
      ],
      "efforts": {
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "defaultEffort": "medium",
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text"
      ],
      "note": "\u9636\u8dc3 Step \u6863\u4f4d\uff1aLow / Medium / High\uff08\u9ed8\u8ba4 Medium\uff0c\u4e0d\u53ef\u5173\u95ed\uff09\u30023.6/3.7 \u89c6\u89c9\u4ee3\u89c1\u5355\u72ec\u6761\u76ee\u3002"
    },
    {
      "id": "doubao",
      "patterns": [
        "doubao",
        "seed"
      ],
      "efforts": {
        "off": null,
        "low": "low",
        "medium": "medium",
        "high": "high"
      },
      "compat": {
        "thinkingFormat": "openai",
        "supportsReasoningEffort": true
      },
      "input": [
        "text",
        "image"
      ],
      "note": "\u8c46\u5305\u6863\u4f4d\uff1aOff / Low / Medium / High\u2014\u2014effort \u9636\u68af\u4ecd\u662f\u793e\u533a\u8bc1\u636e\u3001\u5b98\u65b9 Ark \u6587\u6863\u660e\u5217\u7684\u4e3a thinking.type \u5f00\u5173\uff082026-08-24 \u590d\u6838\u4ecd\u672a\u89c1\u5230 effort \u5b98\u65b9\u660e\u6587\uff09\u3002seed \u4ee3\u6536\u56fe\uff081.5-pro \u4f8b\u5916\uff09\u3002"
    },
    {
      "id": "minimax-m3",
      "patterns": [
        "minimax-m3"
      ],
      "efforts": {
        "off": null,
        "high": "high"
      },
      "compat": {
        "thinkingFormat": "deepseek"
      },
      "input": [
        "text",
        "image"
      ],
      "contextWindow": 1048576,
      "note": "MiniMax-M3\uff1a\u5b98\u65b9 thinking \u53c2\u6570 enabled/adaptive/disabled\uff08\u65e0 effort \u6863\uff09\uff0c\u5f00=High\u3001\u5173=disabled\uff1b\u539f\u751f\u591a\u6a21\u6001\uff08\u56fe/\u89c6\u9891\uff0c\u6838\u5fc3\u8bcd\u8868\u4ec5\u542b\u56fe\uff09\uff0c1M \u4e0a\u4e0b\u6587\u3002"
    },
    {
      "id": "baidu-ernie",
      "patterns": [
        "ernie"
      ],
      "efforts": false,
      "input": [
        "text"
      ],
      "contextWindow": 131072,
      "note": "\u767e\u5ea6\u5343\u5e06 ERNIE \u7cfb\uff1a\u5b98\u65b9 OpenAI \u517c\u5bb9\u63a5\u53e3\u65e0 reasoning_effort \u53c2\u6570\u2014\u2014\u601d\u8003\u7531\u6a21\u578b\u53d8\u4f53\u51b3\u5b9a\uff08-Thinking \u7cfb\u5217\u59cb\u7ec8\u601d\u8003\u3001\u666e\u901a\u7cfb\u5217\u4e0d\u601d\u8003\uff09\uff0c\u52ff\u52fe\u601d\u8003\u6863\u3002ERNIE 4.5 Turbo VL \u652f\u6301\u56fe\u7247\uff0c\u6309\u9700\u624b\u52fe\uff1b\u53c2\u8003\u5bb9\u91cf\u53d6 Turbo 128K \u6863\u3002"
    }
  ]
}
/* CK-EFFORT-KNOWLEDGE:END */



/**
 * Resolve one model id (and optional display name) to its table entry.
 *
 * Longest boundary match wins, exactly as upstream: normalisation folds every
 * non-alphanumeric run to one space, and a pattern only counts when it sits on
 * an alphanumeric boundary, so `glm-5.3-free` resolves to the `glm-5-3`
 * entry rather than to the shorter `glm` one.
 */
export const matchEffortKnowledge =
/* CK-EFFORT-MATCH:BEGIN */
(modelId, displayName) => {
  const KNOWLEDGE_BASE = EFFORT_KNOWLEDGE.entries
function isAlnum(ch) {
  return ch !== void 0 && /[a-z0-9]/.test(ch);
}
function normalizeLoose(value) {
  return value.toLowerCase().trim().replace(/[^a-z0-9]+/g, " ");
}
function onBoundary(haystack, at, length) {
  const before = at === 0 ? void 0 : haystack[at - 1];
  const after = haystack[at + length];
  return !isAlnum(before) && !isAlnum(after);
}
function matchKnowledgeBase(modelId, displayName) {
  const haystack = normalizeLoose(modelId) + " " + normalizeLoose(displayName ?? "");
  let best;
  for (const entry of KNOWLEDGE_BASE) {
    for (const pattern of entry.patterns) {
      const needle = normalizeLoose(pattern);
      let at = haystack.indexOf(needle);
      while (at >= 0) {
        if (onBoundary(haystack, at, needle.length)) {
          if (best === void 0 || needle.length > best.length) {
            best = { entry, length: needle.length };
          }
          break;
        }
        at = haystack.indexOf(needle, at + 1);
      }
    }
  }
  return best?.entry;
}
  return matchKnowledgeBase(modelId, displayName)
}
/* CK-EFFORT-MATCH:END */
