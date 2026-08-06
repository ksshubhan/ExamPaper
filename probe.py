import json, anthropic, sympy

client = anthropic.Anthropic()
MODEL = "claude-opus-4-8"
N_RUNS = 10

PROMPT = """Generate one AQA Higher-tier GCSE maths question on {topic}.
Return ONLY JSON, no prose, no markdown fences, with keys:
  "question_text": the question as a student would see it,
  "stated_answer": the final numeric answer as a string,
  "check_expr": a single sympy-parseable expression that computes the
                answer from scratch (e.g. "sqrt(8**2 + 6**2)").
The check_expr must derive the answer independently, not just restate it."""

def probe(topic, n=N_RUNS):
    passes = 0
    for i in range(n):
        msg = client.messages.create(
            model=MODEL, max_tokens=1000,
            messages=[{"role": "user", "content": PROMPT.format(topic=topic)}],
        )
        q = None
        try:
            q = json.loads(msg.content[0].text)
            computed = sympy.nsimplify(sympy.sympify(q["check_expr"]))
            stated = sympy.nsimplify(sympy.sympify(q["stated_answer"]))
            ok = sympy.simplify(computed - stated) == 0
        except Exception as e:
            ok = False
            print(f"  [{i}] error: {e}")
        passes += ok
        label = q["question_text"][:70] if q else ""
        print(f"  [{i}] {'PASS' if ok else 'FAIL'} — {label}")
    print(f"\n{topic}: {passes}/{n} verified")

probe("Pythagoras' theorem")
