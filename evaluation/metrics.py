def hit_at_k(pred,gold,k): return float(gold in pred[:k])
def mrr(pred,gold):
    return 1/(pred.index(gold)+1) if gold in pred else 0.0
