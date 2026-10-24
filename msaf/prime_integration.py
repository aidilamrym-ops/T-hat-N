from msaf import precision, certify, operators
from msaf.prime_bridge.sieve_flow import prime_pi, segmented_sieve
from msaf.prime_bridge.feature   import gaps, gap_histogram, dirichlet_sums
from msaf.prime_bridge.learner   import train, predict
from msaf.prime_bridge.ai_insight import extract_conjecture

def prime_data_bundle(N: int):
    primes = segmented_sieve(N)
    g      = gaps(primes)
    hist   = gap_histogram(g, bins=20)
    dirich = dirichlet_sums(primes, moduli=[3,5,7,11])
    return {
        "primes": primes,
        "gap_list": g,
        "gap_hist": hist,
        "dirichlet": dirich,
    }

def generate_conjecture(N: int):
    data   = prime_data_bundle(N)
    vector = {
        "gap_hist": [(i, c) for i, c in enumerate(data["gap_hist"][1])],
        "modulus": 5,
    }
    model  = train([vector])
    stmt   = predict(model, vector)
    ai_res = extract_conjecture(N, len(data["primes"]), data["gap_list"])
    statement = f"{stmt}  --  AI confidence {ai_res['confidence']:.2f}"
    return statement, ai_res["confidence"]

def certify_prime_conjecture(N: int):
    stmt, conf = generate_conjecture(N)
    payload = {
        "schema": "msaf.prime_conjecture.v1",
        "statement": stmt,
        "confidence": conf,
        "bound": N,
    }
    return payload
