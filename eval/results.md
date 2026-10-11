# Evaluation results

Model: `openai/gpt-oss-120b`

**Pass rate: 10/12 (83%)**

| # | Result | Tools used | Problems |
|---|---|---|---|
| 1 | PASS | search_policy, calculate |  |
| 2 | PASS | search_policy, calculate |  |
| 3 | PASS | search_policy, calculate |  |
| 4 | PASS | search_policy, convert_currency, calculate |  |
| 5 | PASS | search_policy, convert_currency, calculate |  |
| 6 | PASS | search_policy |  |
| 7 | PASS | search_policy |  |
| 8 | PASS | search_policy |  |
| 9 | PASS | search_policy |  |
| 10 | PASS | search_policy, convert_currency, calculate |  |
| 11 | FAIL |  | exception: Error code: 401 - {'error': {'message': 'Invalid API Key', 'type': 'invalid_request_error', 'code': 'invalid_api_key'}} |
| 12 | FAIL |  | exception: Error code: 401 - {'error': {'message': 'Invalid API Key', 'type': 'invalid_request_error', 'code': 'invalid_api_key'}} |
