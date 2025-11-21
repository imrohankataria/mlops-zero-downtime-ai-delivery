# Blue/Green Deployment Flow

## Deployment Sequence

### Phase 1: Initial State
```
┌─────────────────────────────────────────┐
│         Load Balancer Service           │
│         (points to BLUE)                │
└─────────────────────────────────────────┘
                  │
                  ↓
         ┌────────────────┐
         │ Blue Deployment│
         │   (ACTIVE)     │ ← 100% Traffic
         │   v1.0.0       │
         │   3 Pods       │
         └────────────────┘

         ┌────────────────┐
         │Green Deployment│
         │   (STANDBY)    │ ← 0% Traffic
         │   v1.0.0       │
         │   3 Pods       │
         └────────────────┘
```

### Phase 2: New Deployment to Green
```
┌─────────────────────────────────────────┐
│         Load Balancer Service           │
│         (points to BLUE)                │
└─────────────────────────────────────────┘
                  │
                  ↓
         ┌────────────────┐
         │ Blue Deployment│
         │   (ACTIVE)     │ ← 100% Traffic
         │   v1.0.0       │
         │   3 Pods       │
         └────────────────┘

         ┌────────────────┐
         │Green Deployment│
         │  (DEPLOYING)   │ ← 0% Traffic
         │   v1.1.0 🚀    │ ← NEW VERSION
         │   Rolling out  │
         └────────────────┘
```

### Phase 3: Health Checks
```
┌─────────────────────────────────────────┐
│         Load Balancer Service           │
│         (points to BLUE)                │
└─────────────────────────────────────────┘
                  │
                  ↓
         ┌────────────────┐
         │ Blue Deployment│
         │   (ACTIVE)     │ ← 100% Traffic
         │   v1.0.0       │
         │   3 Pods       │
         └────────────────┘

         ┌────────────────┐
         │Green Deployment│
         │   (TESTING)    │ ← 0% Traffic
         │   v1.1.0       │
         │   3 Pods       │
         │   Health: ✓✓✓✓✓│ ← 5/5 checks passed
         └────────────────┘
```

### Phase 4: Traffic Switch (Zero Downtime!)
```
┌─────────────────────────────────────────┐
│         Load Balancer Service           │
│      (switching to GREEN) 🔄            │
└─────────────────────────────────────────┘
            │              │
            ↓              ↓
    ┌────────────┐   ┌────────────┐
    │Blue Depl.  │   │Green Depl. │
    │  (DRAINING)│   │(RECEIVING) │
    │  v1.0.0    │   │  v1.1.0    │
    │  50% ↓     │   │  50% ↑     │
    └────────────┘   └────────────┘
```

### Phase 5: New Steady State
```
┌─────────────────────────────────────────┐
│         Load Balancer Service           │
│         (points to GREEN)               │
└─────────────────────────────────────────┘
                  │
                  ↓
         ┌────────────────┐
         │ Blue Deployment│
         │   (STANDBY)    │ ← 0% Traffic
         │   v1.0.0       │ ← Ready for rollback
         │   3 Pods       │
         └────────────────┘

         ┌────────────────┐
         │Green Deployment│
         │   (ACTIVE)     │ ← 100% Traffic
         │   v1.1.0       │
         │   3 Pods       │
         └────────────────┘
```

## Rollback Scenario

### If Health Checks Fail
```
┌─────────────────────────────────────────┐
│         Load Balancer Service           │
│      (STAYS on BLUE) ⚠️                 │
└─────────────────────────────────────────┘
                  │
                  ↓
         ┌────────────────┐
         │ Blue Deployment│
         │   (ACTIVE)     │ ← 100% Traffic (unchanged)
         │   v1.0.0       │
         │   3 Pods       │
         └────────────────┘

         ┌────────────────┐
         │Green Deployment│
         │   (FAILED)     │ ← 0% Traffic
         │   v1.1.0       │
         │   Health: ✓✓✗  │ ← Failed check 3/5
         └────────────────┘

         Action: Deployment aborted, investigate Green
                 No user impact! ✓
```

### Manual Rollback After Traffic Switch
```
Time to Rollback: < 10 seconds

1. Detect Issue (monitoring/alerts)
   └─→ 2. Run: ./scripts/deploy.sh rollback
       └─→ 3. Service selector updated
           └─→ 4. Traffic switches back to Blue
               └─→ 5. Done! Service restored

Old Method (Rolling Update):
- Stop current deployment
- Start new deployment with old version
- Wait for pods to be ready
- Total time: 5-10 minutes ⚠️

Blue/Green Method:
- Update service selector
- Done!
- Total time: < 10 seconds ✅
```

## Key Benefits Visualization

### Zero Downtime During Deployment
```
Traditional Rolling Update:
┌────────────────────────────────────────┐
│ Traffic │████████▒▒▒▒████████▒▒▒▒█████ │ ← Drops during pod restart
│         └─────────────────────────────┘ │
│ Time    0s   30s   60s   90s   120s    │
└────────────────────────────────────────┘
         ⚠️ Potential downtime windows

Blue/Green Deployment:
┌────────────────────────────────────────┐
│ Traffic │████████████████████████████████│ ← Consistent
│         └─────────────────────────────┘ │
│ Time    0s   30s   60s   90s   120s    │
└────────────────────────────────────────┘
         ✅ Zero downtime guaranteed
```

### Resource Usage Comparison
```
Rolling Update:
┌────────────────────────────────────────┐
│Resources│                                │
│ 200%    │         ▄▄▄▄                  │
│ 150%    │      ▄▄▄    ▄▄▄▄             │
│ 100%    │██████          ████████████   │
│  50%    │                                │
│         └─────────────────────────────┘ │
└────────────────────────────────────────┘
         Temporary spikes during deployment

Blue/Green:
┌────────────────────────────────────────┐
│Resources│                                │
│ 200%    │██████████████████             │ ← Both running
│ 150%    │                                │
│ 100%    │                  ████████████  │
│  50%    │                                │
│         └─────────────────────────────┘ │
└────────────────────────────────────────┘
         Higher steady-state, predictable cost
```

## Implementation Details

### Service Selector Magic
The entire blue/green deployment hinges on a single label update:

```yaml
# Before (serving Blue)
spec:
  selector:
    app: ai-model
    deployment: blue  ← Traffic goes to blue pods

# After (serving Green)
spec:
  selector:
    app: ai-model
    deployment: green ← Traffic goes to green pods
```

### Health Check Criteria
Each canary health check validates:
1. ✓ HTTP 200 response from /health endpoint
2. ✓ All pods in Ready state
3. ✓ Response time < 3 seconds
4. ✓ Model loaded successfully
5. ✓ Prediction endpoint functional

If ANY check fails → deployment aborted, no traffic switch

## Cost Analysis

### Example: 3-node cluster, 3 pods per deployment

**Monthly Cost Breakdown:**

Blue/Green (both environments running):
```
Base infrastructure:  $500/month
Blue deployment:      $150/month
Green deployment:     $150/month
Load balancer:        $30/month
─────────────────────────────────
Total:                $830/month
```

Rolling Update (single environment):
```
Base infrastructure:  $500/month
Single deployment:    $150/month
Load balancer:        $30/month
─────────────────────────────────
Total:                $680/month
```

**Additional Cost: ~$150/month (22%)**

**Value Delivered:**
- Zero downtime guarantee
- Instant rollback capability
- Lower operational risk
- Better sleep for ops team 😴

**Break-even Analysis:**
One major incident with traditional deployment:
- 1 hour downtime = potential $10,000+ cost
- Blue/Green pays for itself in < 1 prevented incident per year

## Monitoring During Deployment

### Key Metrics to Watch
```
┌─────────────────────────────────────────┐
│ Deployment Dashboard                    │
├─────────────────────────────────────────┤
│ ● Active Environment:      Green        │
│ ● Standby Environment:     Blue         │
│ ● Traffic Split:           100% / 0%    │
│ ● Response Time:           45ms (✓)     │
│ ● Error Rate:              0.01% (✓)    │
│ ● Pod Health:              6/6 Ready    │
│ ● Last Deployment:         2m ago       │
│ ● Last Rollback:           Never        │
└─────────────────────────────────────────┘
```

### Alert Thresholds
- Response time > 100ms → Warning
- Error rate > 1% → Critical, consider rollback
- Pod health < 100% → Warning
- Failed health check → Abort deployment

## Best Practices

1. **Always test in staging first** - Use same blue/green setup in staging
2. **Automate health checks** - Don't rely on manual verification
3. **Monitor after switch** - Watch metrics for 5-10 minutes post-deployment
4. **Keep rollback ready** - Don't delete old deployment immediately
5. **Document rollback procedures** - Ensure team knows how to rollback
6. **Regular drills** - Practice rollback procedures quarterly
7. **Gradual rollout** - Consider canary deployments for extra safety

## Troubleshooting

### Common Issues

**Issue: Health checks failing**
- Check pod logs: `kubectl logs -n ai-model-serving -l deployment=green`
- Verify service endpoints: `kubectl get endpoints -n ai-model-serving`
- Check resource limits: Pods might be OOMKilled

**Issue: Traffic not switching**
- Verify service selector: `kubectl describe svc ai-model-service -n ai-model-serving`
- Check service labels match pod labels
- Verify endpoints are populated

**Issue: Slow rollback**
- Ensure old deployment is still running
- Check if pods in standby are healthy
- Verify network connectivity

## Future Enhancements

Possible additions to this implementation:
- [ ] Canary deployments (gradual traffic shift)
- [ ] A/B testing support
- [ ] Progressive delivery with feature flags
- [ ] Automated performance testing before switch
- [ ] Integration with observability platforms
- [ ] Slack/Teams notifications
- [ ] Cost tracking and reporting
- [ ] Multi-region blue/green
