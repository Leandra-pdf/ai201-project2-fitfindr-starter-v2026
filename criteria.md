# Acceptance criteria — FitFindr

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

## 3. Search relevance**

Given a query and multiple listings where the strongest match appears in the listing's `title` or `style_tags` rather than its `description`, `search_listings` ranks the strongest matching listing ahead of weaker matches in 5 out of 5 tries.

**Why this target:**

I chose 5 out of 5 because search relevance should be consistent across repeated runs. The current ranking logic compares query keywords against listing keywords from the description, ignoring the title and style tags. This test checks whether the search results reflect the most relevant listing rather than simply the greatest keyword overlap in the description.

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

## **6. Weighted reranking prioritizes stronger matches**

Given a query and multiple listings where the strongest match appears in the listing's `title` or `style_tags` rather than its `description`, the reranking logic places the strongest matching listing ahead of weaker matches in 5 out of 5 controlled test cases.

**Why this target:**

I chose 5 out of 5 because the ranking logic uses fixed weights for title, style tags, and description matches. Given the same query and listings, the strongest match should consistently receive the highest score. This tests whether the new weighted ranking actually prioritizes the most relevant listings.

---

## **7. Reranking preserves price and size filters**

Given queries with a maximum price or requested size, every listing returned by the reranking process satisfies the specified price and size restrictions in 10 out of 10 test cases.

**Why this target:**

I chose 10 out of 10 because reranking should only change the order of matching listings, not which listings are allowed through the filters. Returning an item over someone's budget or in the wrong size would make the search results misleading. These restrictions are deterministic, so I expect them to be respected every time.

---

## **8. Deployed searches meet a response-time target**

Given 10 valid search requests to the deployed `/ask` endpoint, at least 9 out of 10 complete within 5 seconds, as measured by the request duration in the application logs.

**Why this target:**

I chose 9 out of 10 because new searches take longer to run. Five seconds gives the user a reasonable wait time while allowing for delays. Measuring the duration through the logs also tests whether the instrumentation provides useful performance information.

---

## **9. Deployed endpoints return expected responses**

Given 10 requests to the deployed `/health` and `/ask` endpoints using valid inputs, all 10 return HTTP 200 responses with the expected response structure.

**Why this target:**

I chose 10 out of 10 because these are basic endpoint requirements. The health endpoint should confirm that the application is running, and the ask endpoint should return a successful response for valid searches. A failed request would indicate a deployment or application problem that should be investigated.

---

## **10. Failed requests are captured in the logs**

Given 5 requests that intentionally trigger errors, all 5 produce log entries containing the request path, duration, HTTP status, and error information.

**Why this target:**

I chose 5 out of 5 because logging is intended to help identify and diagnose failures. If a request fails but the logs don't capture what happened, it becomes much harder to investigate problems in the deployed application. Since the application controls its own logging, these details should be recorded consistently.