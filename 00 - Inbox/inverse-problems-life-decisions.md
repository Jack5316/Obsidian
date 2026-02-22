---
title: Life Decisions as Inverse Problems
link: life-decisions-inverse-problems
tags: thinking, math, decisions
make_discoverable: true
lang: en
meta_description: Important decisions are inverse problems — you know the outcome you want but not the inputs that produce it. Linear algebra has something to say about that.
---

# Life Decisions as Inverse Problems

*What linear algebra teaches us about the hardest decisions — and where the analogy breaks*

---

## The Easy Direction

In linear algebra, the **forward problem** is trivial. Given a matrix **A** and an input vector **x**, compute **b = Ax**. Multiply, sum, done. A first-year student can do it before coffee.

The **inverse problem** is where things get interesting. You observe **b** — the output, the result, the state of the world you want — and you need to find **x**. What inputs, applied through this system, would produce *that*?

This is the structure of almost every important decision in life.

---

## Choosing Backwards

Think about how most significant decisions actually work. You don't start with a plan and compute the outcome. You start with the outcome — the life you want, the person you want to become, the problem you need solved — and try to reverse-engineer the inputs.

**Forward problem**: I study computer science, take this job, move to this city → what life do I get?

**Inverse problem**: I want a life with creative freedom, financial stability, and meaningful work → what sequence of choices gets me there?

We almost never face the forward problem in real life. We face the inverse one. And inverse problems are, in the precise mathematical sense, *hard*.

---

## Why Inverse Problems Are Hard

In linear algebra, the inverse of a matrix **A** exists only under strict conditions. When it doesn't — when the matrix is **singular** — the equation **Ax = b** either has no solution or infinitely many.

Life decisions suffer from exactly the same pathologies:

**No solution exists.** Some desired outcomes are simply not reachable from your current position. No combination of inputs produces the **b** you want. The honest answer is: this version of the goal is impossible. Choose a different **b**.

**Infinitely many solutions.** Multiple paths lead to the same destination. This sounds liberating but is actually paralyzing. When every path could work, how do you pick one? The math calls this an *underdetermined system*. Life calls it *analysis paralysis*.

**Ill-conditioning.** Small changes in **b** produce wildly different **x**. You thought you wanted to be a lawyer, but what you actually wanted was the *respect* that comes with being a lawyer. A tiny shift in the desired output — from "lawyer" to "respected" — leads to a completely different set of inputs. Ill-conditioned problems punish imprecision in what you actually want.

---

## The Regularization Trick

Mathematicians deal with ill-posed inverse problems through **regularization** — adding constraints that make the solution stable. The most famous is Tikhonov regularization: instead of finding the exact inverse, you find the solution that's *close enough* while also being *simple*.

This is, I think, the deepest lesson for life decisions. You cannot solve the perfect inverse. But you can regularize:

- **Simplicity bias.** Between two paths to roughly the same outcome, pick the simpler one. Fewer moving parts, fewer things to break.
- **Constraint stacking.** Add your values as constraints. Not just "what career gives me money?" but "what career gives me money *and* doesn't require me to lie?" Each constraint shrinks the solution space. That's a feature, not a bug.
- **Iterate, don't invert.** Gradient descent doesn't compute the inverse directly. It takes a step, measures the error, and adjusts. Most good life decisions work the same way — small moves, frequent feedback, course correction.

---

## Where the Analogy Breaks

Here's the honest part: life is not actually a linear system.

**The matrix changes.** In math, **A** is fixed. In life, the system itself evolves. The job market that existed when you started college is not the one that exists when you graduate. You're solving **A(t)x = b** where **A** is a function of time — and you don't know the function.

**You change.** The **b** you wanted at 20 is not the **b** you want at 35. You're not just solving an inverse problem; you're solving one where the target moves because *you* are the target.

**Nonlinearity.** Real life is wildly nonlinear. Small inputs can produce enormous outputs (a single conversation that changes your career). Large inputs can produce nothing (years of effort in the wrong direction). Linear algebra assumes proportionality. Life does not.

**Irreversibility.** Mathematical operations are reversible. Life is not. You can't un-take the job, un-marry the person, un-spend the decade. Every "solution" you try changes the problem itself.

---

## So Is the Analogy Useful?

Yes — but only if you hold it loosely.

The inverse problem framing is valuable because it names something most people feel but can't articulate: **the difficulty of important decisions is structural, not personal.** You're not indecisive because you're weak. You're indecisive because you're facing an ill-posed problem. That's mathematically hard for everyone.

It's also useful because the *mathematical* solutions — regularization, iteration, constraint stacking — map surprisingly well to *practical* decision-making wisdom. Simplify. Add values as hard constraints. Take small steps and measure. Don't try to compute the perfect answer in one shot.

But the analogy becomes dangerous the moment you treat life as a system you can fully model. The beauty of the inverse matrix is its precision. The beauty of a life decision is its irreducible uncertainty. At some point, you close the textbook and jump.

> The forward problem is for computers. The inverse problem is for humans. And the decision to stop computing and start living — that's not in the syllabus.
