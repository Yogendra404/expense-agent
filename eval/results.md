# Evaluation results

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
| 11 | FAIL |  | exception: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m4a6p11fex1t1njzxdwjm6a0` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 199510, Requested 849. Please try again in 2m35.088s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}} |
| 12 | FAIL |  | exception: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m4a6p11fex1t1njzxdwjm6a0` service tier `on_demand` on tokens per day (TPD): Limit 200000, Used 199509, Requested 726. Please try again in 1m41.52s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}} |
