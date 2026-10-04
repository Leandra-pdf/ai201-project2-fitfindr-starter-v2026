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

[1] parse_query
      in:  Find me a Y2K graphic tee under $30 in size S
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 3 items: Y2K Baby Tee — Butterfly Print, Mesh Long-Sleeve Top — Black, Biker Shorts — Black, Shiny
      →    3 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Here are two fun, easy-to-wear outfit ideas featuring your new Y2K Butterfly Baby Tee and pieces from your exi…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: I am so obsessed with this pink and purple Y2K Baby Tee — Butterfly Print that just dropped on my depop for $1…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two fun, easy-to-wear outfit ideas featuring your new Y2K Butterfly Baby Tee and pieces from your existing wardrobe:

### Outfit 1: Effortless Y2K Streetwear
* **Top:** Y2K Baby Tee — Butterfly Print *(New Item)*
* **Bottoms:** Baggy straight-leg jeans, dark wash *(From your wardrobe)*
* **Footwear:** Chunky white sneakers *(From your wardrobe)*
* **Outerwear:** Black cropped zip hoodie *(From your wardrobe)*
* **Accessories:** Black crossbody bag *(From your wardrobe)*

**Why it works:** 
This look leans all the way into the 2000s aesthetic. The fitted, cropped silhouette of the baby tee balances out the volume of the baggy dark-wash jeans. Layering the black cropped zip hoodie on top keeps you warm while showing off the cute waistline of the jeans, and the chunky white sneakers tie the whole retro vibe together.

---

### Outfit 2: Casual Vintage Prep
* **Top:** Y2K Baby Tee — Butterfly Print *(New Item)*
* **Bottoms:** Wide-leg khaki trousers *(From your wardrobe)*
* **Footwear:** Chunky white sneakers *(From your wardrobe)*
* **Outerwear:** Vintage black denim jacket *(From your wardrobe)*
* **Accessory (Suggested addition):** A brown leather belt *(From your wardrobe)*

**Why it works:**
This outfit plays with proportions by pairing the fitted, pink-and-purple graphic tee with structured, wide-leg khaki trousers. Tucking the tee in and adding your brown leather belt adds a touch of polish. Throwing on the vintage black denim jacket and white sneakers keeps it grounded, comfortable, and effortlessly cool for everyday wear.

  Fit card: I am so obsessed with this pink and purple Y2K Baby Tee — Butterfly Print that just dropped on my depop for $18.0! It has the dreamiest fitted crop length and gives off major effortless streetwear vibes when you style it with baggy jeans and a chunky sneaker.

```

**The three tools, tested one at a time**

```
$ python3 -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017','title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price':26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]

```

```
$ python3 -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Here are two practical, stylish outfits featuring your new Vintage Levi's 501 Jeans:

Outfit 1: Casual & Cool Streetwear
- Top: White ribbed tank top (From your wardrobe)
- Outerwear: Vintage black denim jacket (From your wardrobe)
- Shoes: Chunky white sneakers (From your wardrobe)
- Accessory: Black crossbody bag (From your wardrobe)

Why it works:
This is an effortless, classic combination. The fitted white ribbed tank creates a great balance against the relaxed straight leg of the Levi's 501s. Tossing on the vintage black denim jacket adds a cool double-denim contrast, while the chunky white sneakers and crossbody bag keep the look comfortable and ready for everyday errands.

Outfit 2: Cozy Layered Edge
- Top: Oversized grey crewneck sweatshirt (From your wardrobe)
- Accessory: Brown leather belt (From your wardrobe)
- Shoes: Black combat boots (From your wardrobe)
- Accessory (Optional): Black crossbody bag (From your wardrobe)

**Why it works:**
Tuck the front of your oversized grey crewneck into the 501s and define the waist with your brown leather belt for a polished yet relaxed silhouette. Pairing medium-wash denim with black combat boots instantly adds a touch of streetwear edge, making this the perfect comfortable-yet-put-together outfit for cooler weather.

```

```
$ python3 -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('White ribbed tank top, black denim jacket, and chunky white sneakers', load_listings()[0]))"

I'm still not over finding these Vintage Levi's 501 Jeans in a Medium Wash on depop for just $38.0. That ideal indigo fading at the knees gives them the ultimate lived-in streetwear edge without trying too hard. Toss them on with a crisp white ribbed tank top, a black denim jacket, and chunky white sneakers for the easiest everyday uniform.

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

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



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
