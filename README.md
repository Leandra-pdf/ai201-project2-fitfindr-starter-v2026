# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is an AI-powered secondhand outfit discovery tool where users provide descriptive keywords along with optional size and budget preferences. In return, the agent delivers matching thrift listings, personalized outfit combinations paired with items from their existing wardrobe (or general styling advice if the wardrobe is empty), and a social media-ready style caption. If no listings match, it explains what the user can change to improve the search.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listings data for items matching the requested description, with optional filtering by size and maximum price.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None). `size` and `max_price` are optional. Size matching is case-insensitive and should match the requested size against the listing's size, including combined sizes such as S/M.
- **Returns:** A list of matching listing dictionaries. The best match first. Each listing contains `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None), and `platform`.
- **When it has nothing:** Returns an empty list when no listings match.

### `suggest_outfit`

- **What it does:** Suggests outfit combinations using the user's wardrobe and a thrifted item.
- **Inputs:** `new_item` (dict), a listing dictionary for the item being considered. `wardrobe` (dict), containing an `items` key with a list of wardrobe items.
- **Returns:** Outfit suggestions in a non-empty string.
- **When it has nothing:** If the wardrobe's `items` list is empty, returns general styling advice rather than an error or an empty string.

### `create_fit_card`

- **What it does:** Creates a short social media style caption for the selected item and suggested outfit.
- **Inputs:** `outfit` (str), the outfit suggestion returned by `suggest_outfit()`. `new_item` (dict), the listing dictionary for the selected item.
- **Returns:** A caption that is 2-4 sentences long that read like a real post. It mentions the item, price, and platform once and describes the outfit's vibe.
- **When it has nothing:** If `outfit` is empty or contains only whitespace, returns a descriptive message rather than raising an error.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If the search returns no listings, FitFindr saves a message explaining what the user could change and stops without generating an outfit or fit card. If listings are found, it selects the first result, uses it to generate outfit ideas with the user's wardrobe, and then creates a caption.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** The `parse_query()` function uses regular expressions to pull out the clothing description, optional size, and maximum price from the user's search.

**What moves through the session:** The parsed query is saved in `session["parsed"]`, and the search results go into `session["search_results"]`. If a match is found, the selected listing is saved in `session["selected_item"]` and passed along to generate `session["outfit_suggestion"]` and `session["fit_card"]`. If nothing matches, the agent saves a helpful message in `session["error"]` and leaves `session["fit_card"]` as `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python3 app.py ask 'Find me a Y2K graphic tee under $30 in size S'

Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two cute, easy-to-put-together outfits featuring your new Y2K Butterfly Baby Tee, utilizing pieces you already own!

### Outfit 1: Casual Y2K Streetwear
* **Top:** Y2K Baby Tee — Butterfly Print (New item)
* **Bottoms:** Baggy straight-leg jeans, dark wash *(from your wardrobe)*
* **Footwear:** Chunky white sneakers *(from your wardrobe)*
* **Outerwear (optional):** Black cropped zip hoodie *(from your wardrobe)*
* **Accessories:** Black crossbody bag *(from your wardrobe)*

**Why it works:** 
This outfit plays on the classic Y2K silhouette by pairing a tight, cropped baby tee with loose, baggy denim for a balanced and effortless look. The chunky sneakers andblack crossbody bag tie the retro theme together, and you can easily layer the black cropped zip hoodie over top if it gets chilly.

---

### Outfit 2: Sweet & Casual Contrast
* **Top:** Y2K Baby Tee — Butterfly Print (New item)
* **Bottoms:** Wide-leg khaki trousers *(from your wardrobe)*
* **Accessories:** Brown leather belt *(from your wardrobe)*
* **Footwear:** Chunky white sneakers *(from your wardrobe)*
* **Outerwear (optional):** Vintage black denim jacket *(from your wardrobe)*

**Why it works:**
The butterfly baby tee leans into a playful, vintage aesthetic, which looks great contrasted against the tailored, earthy vibe of the wide-leg khaki trousers. Tucking in the tee and adding the brown leather belt pulls the waist in for a polished shape, while the white sneakers keep the overall feel light, comfortable, and modern.

  Fit card: I am obsessed with the pink and purple butterfly graphic on this Y2K Baby Tee — Butterfly Print, which gives off the sweetest early 2000s energy. It has that perfectly fitted crop length and is listed on depop right now for just $18.0. Style it with baggy dark-wash jeans and chunky sneakers for an effortless streetwear look, or contrast the vintage vibe with wide-leg khaki trousers and a brown leather belt.

2 model calls this session, 853 prompt + 447 output tokens

```

**The three tools, tested one at a time**

```
$ python3 -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category':'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]

```

```
$ python3 -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Here are two stylish, easy-to-wear outfit ideas featuring your new Vintage Levi's 501 Jeans, utilizing pieces you already own.

### Outfit 1: Casual & Sporty Streetwear
* **New Item:** Vintage Levi's 501 Jeans — Medium Wash
* **From your wardrobe:** 
  * White ribbed tank top
  * Oversized grey crewneck sweatshirt
  * Chunky white sneakers
  * Black crossbody bag
* **Why it works:** This is a classic, effortless everyday look. The fitted white tank paired with the straight-leg 501s creates a great silhouette, while the oversizedgrey crewneck layered on top adds that relaxed, streetwear vibe. Finishing with chunky white sneakers and a black crossbody keeps it practical and comfortable for running errands or casual hangouts.

---

### Outfit 2: Edgy Layered Denim
* **New Item:** Vintage Levi's 501 Jeans — Medium Wash
* **From your wardrobe:** 
  * White ribbed tank top
  * Black cropped zip hoodie
  * Vintage black denim jacket
  * Black combat boots
  * Brown leather belt
* **Why it works:** Double denim is having a major moment, and mixing a black denim jacket with medium-wash blue jeans creates a cool, high-contrast look. Tucking in the white ribbed tank (accented with your brown leather belt to tie in some warmth) and layering the cropped hoodie under the jacket adds dimension and texture. Grounding the outfit with black combat boots leans into the edgy, vintage aesthetic.

```

```
$ python3 -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('White ribbed tank top, black denim jacket, and chunky white sneakers', load_listings()[0]))"

I just scored these Vintage Levi's 501 Jeans in a Medium Wash on depop for $38.0, and the knee fading gives them that effortlessly lived-in streetwear vibe. I’m stylingthis blue denim with a crisp white ribbed tank top, a black jacket, and chunky sneakers for the ultimate casual look.

```

---

## How I Used AI

**Moment 1 — Fixing the price parser**

* **What I asked for:** I asked ChatGPT for help figuring out why my query parser wasn't correctly handling searches like `designer ballgown size XXS under $5`.
* **What came back:** It suggested changing the regular expression so it could recognize price limits like `under $5` and extract the number correctly.
* **What I changed:** My first attempt at updating the expression caused a `TypeError` because I passed the arguments to `re.compile()` incorrectly. I fixed the expression and price extraction, then ran the agent again to check that the $5 limit was recognized.

**Moment 2 — Fixing the size parsing error**

* **What I asked for:** I asked ChatGPT for help figuring out why my agent was crashing with an `AttributeError` involving `startswith` when processing a clothing search.
* **What came back:** We traced the issue to `tools.py`, where I had written `.upper` instead of `.upper()`. This meant Python was storing a method reference instead of the uppercase string I needed.
* **What I changed:** I added the missing parentheses to call `.upper()` and return the actual string. I then checked the code to make sure size tokens such as `S/M` were split and processed correctly.


<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion                                           | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict       |
| --------------------------------------------------- | ------ | ----- | ----- | ----- | ----- | ----- | ------------- |
| 1. A matching query completes all three tools       | 4/5    | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 2. An impossible query stops before the second tool | 5/5    | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 3. State preserves the selected listing             | 5/5    | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 4. Fit card varies and meets content requirements   | 2/3    | PASS  | PASS  | PASS  | —     | —     | **MET — 3/3** |
| 5. Search respects the maximum price                | 5/5    | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |

**Note:** Criterion 4 is written as a 3-run criterion rather than a 5-run criterion, because the original requirement specifically says "at least 2 of 3 runs." The three fresh runs were performed with the cache disabled.

**Real output from one try**, pasted as text, naming the file and function that produced it:

```

[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}

[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 8 items: Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print, Vintage Graphic Hoodie — Faded Black … +5 more
      →    8 match(es)

[3] select_item
      out: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)

[4] suggest_outfit
      in:  Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
      out: Here are two effortless, grunge-leaning outfits featuring your new graphic tee and pieces straight from your w…

[5] create_fit_card
      in:  Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
      out: Just scored this perfectly faded Graphic Tee — 2003 Tour Bootleg Style on depop for $24.0, and it has that ult…
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion                                        | Target | Verdict       | How I decided                                                                                                                                                         |
| - | ------------------------------------------------ | ------ | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | A matching query completes all three tools       | 4/5    | **MET — 5/5** | All five matching-query tries completed `search_listings`, `suggest_outfit`, and `create_fit_card` and returned a fit card.                                           |
| 2 | An impossible query stops before the second tool | 5/5    | **MET — 5/5** | All five impossible-query tries returned an empty search result and stopped before `suggest_outfit`, while returning a message explaining what the user could change. |
| 3 | State preserves the selected listing             | 5/5    | **MET — 5/5** | In all five checks, `search_results[0]["id"]` and `selected_item["id"]` were both `lst_006`.                                                                          |
| 4 | Fit card varies and meets content requirements   | 2/3    | **MET — 3/3** | With the cache disabled, all three runs produced different captions. Each caption was 2–4 sentences and mentioned the item, price, and platform.                      |
| 5 | Search respects the maximum price                | 5/5    | **MET — 5/5** | All five searches returned only listings priced at or below the requested $30 maximum.                                                                                |

**Diagnoses**

The results suggest that the empty-search branch, selected-item state handling, and price filtering behaved as expected in the tested cases. The fit-card test also met its variation and content requirements across the three runs.

However, some targets could be stricter. Criterion 1 allows one failure out of five, even though the agent completed all three tools in every observed run. I would consider tightening this criterion to require success in all five runs. Criterion 4 could also be tested on several different listings, including items with missing optional fields, to check whether the caption requirements hold beyond one fixed item and outfit.

These results apply to the tested queries and inputs but they do not prove that the agent will behave accurately for every possible query.



---

## Loop Trace

**Happy path**

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 8 items: Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print, Vintage Graphic Hoodie — Faded Black … +5 more
      →    8 match(es)
[3] select_item
      out: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
[4] suggest_outfit
      in:  Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
      out: Here are two effortless, grunge-leaning outfits featuring your new graphic tee and pieces straight from your w…
[5] create_fit_card
      in:  Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)
      out: Just scored this perfectly faded Graphic Tee — 2003 Tour Bootleg Style on depop for $24.0, and it has that ult…
```

**Empty search**

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    0 match(es)

  Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.
```

**On the MCP move:** I moved `search_listings` from a direct Python function call to an MCP tool registered in `mcp_server.py`. In `agent.py::run_agent`, the agent now calls `call_tool("search_listings", {...})` through `mcp_client.py`. The tool's inputs and returned listing dictionaries remain the same. After the change, the normal query still completed all five trace steps, and the empty-search query still stopped after the search returned an empty list. The traces confirm that the MCP call is working and the agent's branch behavior remains intact.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
