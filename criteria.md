# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**

I chose 4 out of 5 because the search relies on keywords, so it might miss some requests even when a similar listing exists. I still want the agent to complete the whole workflow most of the time when there is a matching item.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**

I chose 5 out of 5 because the agent should be able to tell when a search returns no results and stop instead of moving on to the next tool. There is no model-generated decision involved in determining whether the search returned an empty list, so this behavior should be consistent every time.

---

## 3. Something about state

Given a query that returns at least one listing, the `id` of the first listing returned by `search_listings` matches the `id` of the `new_item` received by `suggest_outfit` in 5 of 5 tries.

**Why this target:**

I chose 5 out of 5 because the agent needs to keep track of the item it found and pass that same item to the next tool. Checking the IDs makes it easy to verify that the correct listing is being used every time.

---

## **4. Something about the fit card**

Given the same valid outfit and listing, `create_fit_card` returns a different caption on at least 2 of 3 runs while every caption is 2 to 4 sentences and mentions the item, price, and platform.

**Why this target:**

I picked 2 of 3 runs because the model is expected to vary its wording, but it does not need to produce completely different wording every time. The item, price, and platform should remain consistent even when the wording changes because those details are required parts of the fit card.

---

## **5. The search respects the maximum price**

Given a query with a specified maximum price, every listing returned by `search_listings` has a price less than or equal to the requested maximum price — in 5 of 5 tries.

**Why this target:**

I picked 5 out of 5 because the price limit is a clear requirement, not something the agent should guess at. If someone sets a maximum price, I expect every result to stay within that budget, every time.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
