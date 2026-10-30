| Policy | Runs | Final correct | Known-stale commit | World-stale commit | Superseded notification* | Stable latency (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| wait | 1764 | 100.00% | 0.00% | 10.88% | 23.94% | 600.0 |
| eager | 1764 | 100.00% | 0.00% | 12.24% | 69.58% | 66.7 |
| guarded_0 | 1764 | 100.00% | 0.00% | 9.52% | 43.78% | 66.7 |
| guarded_200 | 1764 | 100.00% | 0.00% | 8.84% | 34.52% | 200.0 |
| guarded_500 | 1764 | 100.00% | 0.00% | 7.48% | 20.63% | 500.0 |
| guarded_no_fence | 1764 | 79.37% | 55.10% | 62.13% | 100.00% | 66.7 |

*Among revision/cancellation/chain scenarios; retrospective, not necessarily unauthorized at emission.
