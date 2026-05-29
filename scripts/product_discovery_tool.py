import re
from urllib.parse import urlparse
from datetime import date, datetime, timezone
from langchain_core.messages import SystemMessage, HumanMessage

#--------DEBUG-----------
from pathlib import Path  
#------------------------
            
'''QUESTION_GENERATION_PROMPT = """
You are a sex toys vendor.

Your job is to ask ONE question to the customer

Return only:
1. A brief recap of the user preferences and introduce the new question that would help to narrow the choices available
2. the next question
3. an optional choice list

If choices are provided, introduce them exactly with:
"If you're not sure, here are some choices:"

## Style note:
- The brief recap should start with "so you..." and end with variations of "Could you tell me..."

## Core rules

* Ask only ONE question.
* Do NOT mention specific product names.
* Do NOT repeat questions that are under PREVIOUS QUESTIONS AND ANSWERS section.
* Do NOT ask about a preference dimension that was already covered.
* Options shown but not selected are NOT user preferences.
* Do NOT ask about unselected previous options unless the user later mentions them.
* If there are no previous questions do not return A brief description of what you and the user have covered so far

## DIMENSIONS
- Areas of stimulations: penis, clitoris, vulva, G-spot, anus, prostate
- sensations: vibration, sliding, heat, filling
- size: big, small, pocket size, medium, adjustable
- intensity: high, gentle, multi-pattern, remote-control



## Product-type restriction

During questioning, do NOT mention product categories such as:

If retrieved chunks suggest a product type, use that only to infer a preference dimension.

## State rules

* 🐱 means vulva / clitoris / G-spot related preferences
* 🍆 means penis-related preferences
* 🍩 means anal / prostate related preferences
* 🫂 means partner or couples play preferences

Do NOT offer unrelated body-area paths again unless the user explicitly changes direction.

## Choice rules

Choices must:
* be 3 to 5 bulletpoints
* be concrete and first-person
* map clearly to retrieval signals
* avoid duplicates or near-duplicates
* stay inside the selected path
* avoid vague fallback options

Do NOT use choices like:
* A mix of both
* I'm not sure yet
* External stimulation
* Internal stimulation
* Full-body sensations
* Specific areas

If a combined preference is useful, describe it concretely.

Good:
* I'd like both outside touch and inside pleasure

Bad:
* A mix of both


## Examples

Good first question:

What kind of pleasure are you curious to explore?

If you're not sure, here are some choices:
* I'd like to explore vaginal, G-spot or clitoris stimulation 🐱
* I'd like to try some anal play 🍩
* I want to enhance penis stimulation 🍆
* I'd like something for couple play 🫂



""".strip()

'''

FIRST_MESSAGE = """Hello! I'm here to help you choose your new adventorous companion! Let's start with a simple question..."""

PRODUCT_URL_RE = re.compile(r"^a[a-z0-9-]*g[a-z0-9-]*\.html$", re.I)

MAX_CHARS_PER_PRODUCT = 10000

MAX_CHARS_PER_SOURCE_SIGNAL = 10000

QUESTION_GENERATION_PROMPT = """
You are a sex toys vendor.

Your job is to ask ONE question to the customer

Return only:
1. A brief recap of the user preferences and introduce the new question that would help to narrow the choices available
2. the next question
3. an optional choice list

If choices are provided, introduce them exactly with:
"If you're not sure, here are some choices:"

## Style note:
- The brief recap should start with "I'm searching around to find a product that..." + user preferences 
- The brief recap should NOT appear for the FIRST QUESTION
- The question should start on a new line with "Could you tell me..."

## Core rules

* Ask only ONE question 
* Do NOT mention specific product names.
* Do NOT repeat questions that are under PREVIOUS QUESTIONS AND ANSWERS section.
* Do NOT ask about a preference dimension that was already covered.
* Options shown but not selected are NOT user preferences.
* Do NOT ask about unselected previous options unless the user later mentions them.
* If there are no previous questions do not return A brief description of what you and the user have covered so far
* Refer to the provided product taxonomy to generate the next question and narrow the possible products the costumer might be interested



## Examples

Good first question:

What kind of pleasure are you curious to explore?

If you're not sure, here are some choices:
* I'd like to explore vaginal, G-spot or clitoris stimulation 🐱
* I'd like to try some anal play 🍩
* I want to enhance penis stimulation 🍆
* I'd like something for couple play 🫂


## PRODUCT TAXONOMY ##

# Vibrators

## Clitoral Suction Vibrators
- Features: air-pulse, contactless stimulation, focused pleasure, low friction, quiet, precise external stimulation  
- Erogenous areas: clitoris, vulva  

## Womanizer
- Features: Pleasure Air Technology, premium design, contactless clitoral stimulation, smooth intensity control, quiet motor  
- Erogenous areas: clitoris, vulva  

## Clitoral Vibrators
- Features: direct external vibration, focused stimulation, compact, beginner-friendly, customizable intensity  
- Erogenous areas: clitoris, vulva, nipples  

## Rabbit Vibrators
- Features: dual stimulation, internal + clitoral, blended sensations, independent motors, customizable experience  
- Erogenous areas: clitoris, vagina, G-spot  

## Wand Massagers
- Features: powerful vibrations, broad stimulation, deep rumbly sensations, external use, versatile  
- Erogenous areas: clitoris, vulva, nipples, full-body external stimulation  

## G-Spot Vibrators
- Features: curved shape, targeted internal pressure, ergonomic design, focused stimulation, deep sensations  
- Erogenous areas: G-spot, vagina  

## Bullet Vibrators
- Features: compact, pinpoint stimulation, discreet, portable, strong vibrations  
- Erogenous areas: clitoris, nipples, perineum, penis shaft, external anal stimulation  

## App & Remote Controlled Vibrators
- Features: wireless control, app connectivity, long-distance play, customizable patterns, hands-free  
- Erogenous areas: clitoris, vagina, penis, prostate, anal areas, couples/shared stimulation  

## Rose Toys
- Features: flower-shaped design, discreet appearance, compact, clitoral stimulation, social-media popular  
- Erogenous areas: clitoris, vulva  


# Couples Toys

## Couple's Vibrators
- Features: wearable designs, simultaneous stimulation, flexible positioning, hands-free use, synchronized pleasure  
- Erogenous areas: clitoris, vagina, penis, perineum, shared/couples stimulation  

## We-Vibe
- Features: app connectivity, wearable couple designs, remote control, adjustable fit, discreet vibrations  
- Erogenous areas: clitoris, vagina, penis, perineum, shared/couples stimulation  

## Strap-Ons
- Features: harness-compatible, penetrative play, adjustable sizing, roleplay dynamics, wearable designs  
- Erogenous areas: vagina, G-spot, prostate, anal areas, shared/couples stimulation  

## Fun & Foreplay
- Features: teasing, sensory play, massage-focused, playful intimacy, low-pressure exploration  
- Erogenous areas: lips, neck, nipples, thighs, clitoris, penis, full-body stimulation  

## Oral Sex Toys for Couples
- Features: tongue-like stimulation, suction sensations, oral-play enhancement, teasing sensations, partner interaction  
- Erogenous areas: clitoris, vulva, penis, nipples, anal areas  

## Sex Toy Kits
- Features: variety packs, beginner exploration, multi-toy experiences, experimentation, themed collections  
- Erogenous areas: clitoris, vagina, penis, prostate, anal areas, full-body stimulation  

## Rings & Sleeves
- Features: erection support, texture enhancement, shared stimulation, vibrating options, stamina-focused designs  
- Erogenous areas: penis, clitoris, perineum, vagina  



# Penis-Focused Toys

## Cock Rings
- Features: erection support, pressure stimulation, vibrating options, stamina enhancement, shared stimulation  
- Erogenous areas: penis shaft, penis base, perineum, clitoris  

## Blow Job Toys
- Features: suction stimulation, oral-like sensations, textured interiors, hands-free options, rhythmic stimulation  
- Erogenous areas: penis, frenulum, glans  

## Prostate Massagers
- Features: curved shape, targeted internal pressure, hands-free stimulation, vibration patterns, ergonomic design  
- Erogenous areas: prostate, anal areas, perineum  

## Penis Extenders & Sleeves
- Features: textured surfaces, girth enhancement, length extension, wearable designs, shared stimulation  
- Erogenous areas: penis, vagina, anal areas, clitoris  

## Realistic Male Toys
- Features: lifelike textures, realistic orifices, soft materials, immersive sensations, body-inspired designs  
- Erogenous areas: penis, frenulum, glans  

## Male Vibrators
- Features: vibrating stimulation, textured sleeves, hands-free use, customizable intensity, targeted sensations  
- Erogenous areas: penis, frenulum, glans, perineum  

## Penis Pumps
- Features: vacuum pressure, temporary firmness enhancement, sensitivity increase, manual or automatic control  
- Erogenous areas: penis, penis shaft, glans  

## Pocket Pussies
- Features: compact strokers, textured interiors, discreet design, portable use, soft materials  
- Erogenous areas: penis, frenulum, glans  

## Fleshlights
- Features: sleeve-based stimulation, realistic textures, suction control, removable inserts, discreet case design  
- Erogenous areas: penis, frenulum, glans  

# Dildos

## Realistic Dildos
- Features: lifelike shapes, anatomical details, realistic textures, skin-like materials, natural appearance  
- Erogenous areas: vagina, G-spot, anal areas, prostate  

## Non-Realistic Dildos
- Features: abstract designs, smooth shapes, artistic aesthetics, ergonomic curves, non-anatomical appearance  
- Erogenous areas: vagina, G-spot, anal areas, prostate  

## Anal Dildos
- Features: tapered tips, flared bases, firm pressure, anal-safe design, gradual sizing  
- Erogenous areas: anal areas, prostate  

## Large Dildos
- Features: fullness-focused, oversized dimensions, deep pressure, intense stretching sensations, firm structure  
- Erogenous areas: vagina, G-spot, anal areas, prostate  

## Vibrating Dildos
- Features: internal vibration, customizable intensity, blended stimulation, rechargeable options, hands-free potential  
- Erogenous areas: vagina, G-spot, anal areas, prostate  

## Suction Cup Dildos
- Features: hands-free use, strong suction base, versatile positioning, harness compatibility, stable placement  
- Erogenous areas: vagina, G-spot, anal areas, prostate  

## Glass Dildos
- Features: rigid structure, smooth surface, temperature play, firm pressure, non-porous material  
- Erogenous areas: vagina, G-spot, anal areas, prostate  

## Fantasy Dildos
- Features: imaginative designs, non-human aesthetics, textured surfaces, roleplay-focused, creative shapes  
- Erogenous areas: vagina, G-spot, anal areas, prostate  

## G-Spot Dildos
- Features: curved shape, targeted pressure, firm stimulation, ergonomic angle, focused internal contact  
- Erogenous areas: G-spot, vagina  

## Ejaculating Dildos
- Features: fluid-release function, realistic simulation, squeezable reservoirs, roleplay enhancement, immersive experience  
- Erogenous areas: vagina, G-spot, anal areas, prostate  


# Anal Sex Toys

## Butt Plugs
- Features: flared bases, tapered insertion, wearable designs, fullness sensations, long-term comfort  
- Erogenous areas: anal areas, prostate  

## Anal Vibrators
- Features: vibrating stimulation, targeted pressure, curved shapes, adjustable intensity, anal-safe bases  
- Erogenous areas: anal areas, prostate, perineum  

## Anal Beads
- Features: progressive sizing, rhythmic insertion, textured sensations, flexible chains, gradual stimulation  
- Erogenous areas: anal areas  

## Douches & Enemas
- Features: cleansing preparation, squeezable bulbs, shower compatibility, hygiene-focused, preparation support  
- Erogenous areas: anal areas  
"""

QUERY_GENERATION_PROMPT = """
You generate semantic retrieval queries for a vector database containing Lovehoney.eu product descriptions.

Your task is to transform the user's known preferences into a compact semantic product-intent description optimized for embedding similarity search.

The generated text will be embedded and matched against product-description chunks inside ChromaDB.

Rules:

* Return ONLY the retrieval query.
* Do NOT ask questions.
* Do NOT use conversational language.
* Do NOT invent preferences.
* Do NOT mention specific product names or brands unless explicitly provided by the user.
* Focus on semantic meaning rather than search-engine phrasing.
* Include the strongest preference signals available.
* Prefer descriptive product intent over keyword stuffing.

Prioritize:
1. Core product type
2. Desired experience or sensation
3. Use case or context
4. Important practical constraints
5. Secondary refinements

Avoid:
* generic phrases
* vague shopping language
* unnecessary filler
* contradictory attributes
* excessively long enumerations

Emoji meaning normalization:
- Interpret 🐱 as vulva, vagina, clitoris, vaginal pleasure, or clitoral pleasure depending on context.
- Interpret 🍆 as penis, penile pleasure, male sex toys, stroker, masturbator, or prostate-related interest depending on context.
- Interpret 🍩 as anus, anal play, anal sex toys, butt plugs, anal beads, or prostate stimulation depending on context.
- Interpret 🫂 as couples play, partner play, shared pleasure, or toys for couples.
- When generating retrieval queries, replace emojis with plain semantic terms.
- Do not leave emojis in the retrieval query.


Return ONLY the retrieval query.
""".strip()

TAVILY_QUERY_GENERATION_PROMPT = """
                        You generate retrieval queries for Tavily search on Lovehoney.eu.

                        Your task is to convert the user's known preferences into a short, natural search phrase optimized for product retrieval.

                        Rules:
                        - Return ONLY the search query.
                        - Do NOT ask questions.
                        - Do NOT use conversational language.
                        - Do NOT invent preferences.
                        - Do NOT mention specific product names.
                        - Prefer short natural search phrases over long keyword lists.
                        - Include only the most important known preferences.
                        - Prioritize category, sensation, use context, and major practical features.
                        - Avoid stacking too many filters together.
                        - The query should resemble something a human would type into a search engine.

                        Prefer:
                        - compact quiet couples vibrator
                        - beginner anal toys soft silicone
                        - clitoral suction toy travel friendly
                        - powerful wand vibrator rechargeable

                        Avoid:
                        - beginner quiet rechargeable waterproof travel-friendly silicone couples clitoral suction vibrator
                        - What kind of vibrator should I buy?
                        - sex toys for pleasure

                        Return ONLY the query.
                        """.strip()

PRODUCT_RECOMMENDATION_PROMPT = """
                                You are a lovehoney.eu discovery assistant.
                                You will generate a recommendation for the customer

                                Rules:
                                1. Recommend only products included in the provided context.
                                2. Do not answer from memory.
                                3. Do not invent prices, materials, reviews, stock status, or product claims.
                                4. If a detail is not present in the context, omit it.
                                5. Each product recommended should have these sections: name of the product, brief description, features, what other customers say
                                6. Recommend all the products retrieved
                        
                                """.strip() 

TODAY = date.today().isoformat()

class ProductDiscoveryTool:
    def __init__(self, llm=None, search=None, question_context_retriever=None):
        self.llm = llm
        self.search = search  
        self.question_context_retriever = question_context_retriever

        self.project_root = Path(__file__).resolve().parents[1]  
        self.debug_dir = self.project_root / "data"  # Choose debug output folder.
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.debug_markdown_path = self.debug_dir / f"debug_{timestamp}.md"
         
    def utc_timestamp(self):
        return datetime.now(timezone.utc).isoformat()  # Return a stable UTC timestamp for debug logs.
    
    def clean_single_line(self,text):
        """clean the string and return it in single line"""
        text = str(text or "")
        text = text.strip().strip("`").strip()
        text = text.replace("\n", " ")
        text = " ".join(text.split())
        return text.strip('"').strip("'")


#SURVEY INITIALIZATION
    def is_active(self,session): # check whether a saved product discovery session should continue handling messages.
        return bool(
            session and session.get("status") == "asking_questions"
            ) # return True only when a session exists and is still asking questions
    
    def start_session(self):
        """initialize the session"""
        session_initialization = {
            "mode": "product_discovery",
            "status": "not_started",
            "question_index": 0,
            "max_questions": 5,
            "current_question": None,
            "answers": [],
            "query": None,
            "last_product_results": [],
            "sources": [], #source objects used for follow-up grounding
            "last_all_results": [],# latest raw results
            "last_sources": [], #latest summarized source objects
            "latest_sources_summary": "",
            "combined_sources_summaries": [],

        }
        return session_initialization
    
    def generate_first_question(self, session):
        prompt = f"""
        {QUESTION_GENERATION_PROMPT}

        Previous answers:
        []

        Recent Lovehoney discovery signals:
        No user preferences have been collected yet. Generate the first discovery question.
        """.strip()

        response = self.llm.invoke(prompt)
        return response.content.strip()
    
    def start_survey(self, opening_message = FIRST_MESSAGE):
        session = self.start_session()
        session["status"]= "asking_questions"
        first_question = self.generate_first_question(session)
        session["current_question"] = first_question

        return self.build_result(
            question = opening_message or "",
            answer=f"{opening_message}\n\n{first_question}",
            session=session,
        )


#SURVEY PROGRESSION
    def extract_substep_sources(self, results, query, answer_index):
        sources = []  # Collect structured source records for summarization and debugging.
        timestamp = self.utc_timestamp()  # Use one timestamp for this extraction batch.

        for result in results or []:  
            sources.append({
                "title": result.get("title", ""),  
                "url": result.get("url", ""),  
                "content": result.get("content", ""),  
                "raw_content": result.get("raw_content", ""), 
                "score": result.get("score"),  
                "query": query,  
                "timestamp": timestamp,  
                "answer_index": answer_index, 
            })

        return sources  # Return structured substep sources.
    
    def chroma_docs_to_results(self, docs, query):
        results = []
        for doc, relevance_score in docs:
            content = doc.page_content
            metadata = doc.metadata or {}
            results.append({
                "title": metadata.get("title", "Lovehoney product chunk"),
                "url": "",
                "content": content,
                "raw_content": content,
                "score": relevance_score,
                "query": query,
            })
        return results

    def format_sources_for_combined_summary(self, sources):
        blocks = []

        for index, source in enumerate(sources or [], start=1):
            source_text = (source.get("content") or "").strip()

            if not source_text:
                continue

            source_text = source_text[:MAX_CHARS_PER_SOURCE_SIGNAL]

            blocks.append(
                f"Source {index}\n"
                f"Query: {source.get('query', '')}\n"
                f"Title: {source.get('title', '')}\n"
                f"URL: {source.get('url', '')}\n"
                f"Content:\n{source_text}"
            )

        return "\n\n---\n\n".join(blocks)

    def generate_next_question(self, session):
        answers = session.get("answers", [])  # Read the saved discovery answers.
        source_context =session.get("latest_sources_summary", "")
        previous_questions = "\n".join(item.get("question", "") for item in answers if item.get("question"))
        previous_answers = "\n".join(item.get("answer", "") for item in answers if item.get("answer"))

        prompt = f"""
        {QUESTION_GENERATION_PROMPT}

        ## PREVIOUS QUESTIONS
        Do NOT GENERATE these questions again or similar questions:
        {previous_questions}

        ## PREVIOUS ANSWERS
        {previous_answers}

        ## CONTEXT:
        {source_context}
        """.strip()  # Include both user answers and summarized retrieval signals.

        response = self.llm.invoke(prompt)  # Ask the LLM for exactly one next question.
        return response.content.strip()  # Return only the question text.
    
    def save_answer(self, session, question, user_answer):
        session["answers"].append(
            {
                "question": question,
                "answer": user_answer,
            }
        )
        session["question_index"] += 1
        return session
    
    def build_result(self, question, answer, session, sources=""):
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "mode": "product_discovery",
            "status": session["status"],
            "session": session,
        }


#PRODUCT SEARCH
    def search_for_question_context(self, query):
        if self.question_context_retriever is None:
            return []

        clean_query = self.clean_single_line(query)
        docs = self.question_context_retriever.similarity_search_with_relevance_scores(
                                                            clean_query,
                                                            k=10,
                                                        )
        return self.chroma_docs_to_results(docs, clean_query)

    def generate_search_query(self, session):
        if self.llm is None:
            joined_answers = "; ".join(
                f"{item['question']} {item['answer']}" for item in session["answers"]
            )
            session["query"] = joined_answers
            return session["query"]
        answers = session["answers"]
        prompt = f"""
                  {QUERY_GENERATION_PROMPT}
                  
                  User answers:
                  
                  {answers}
                  """.strip()
        response = self.llm.invoke(prompt)
        query = self.clean_single_line(response.content)
        session["query"] = query
        return session["query"]

    def is_product_url(self,url):
        parsed = urlparse(url)
        filename = parsed.path.rstrip("/").split("/")[-1]
        return bool(PRODUCT_URL_RE.match(filename))
    
    def filter_product_results(self,results, min_products=3):
        if not isinstance(results,list):
            return []
        product_results = []
        seen_urls = set()
        for item in results:
            url = item.get("url","")
            if not url or url in seen_urls or not self.is_product_url(url):
                continue
            product_results.append(item)
            seen_urls.add(url)
            if len(product_results) >= min_products:
                break
        return product_results

    def search_products(self, query, min_products = 3):
        if self.search is None:
            return [], []
    
        response = self.search.invoke({"query":query})
        results = response.get("results", []) 
        product_results = self.filter_product_results(results, min_products = min_products)
        return results, product_results


#PRODUCT RECOMMENDATION 

    def generate_tavily_search_query(self, session):
        if self.llm is None:
            joined_answers = "; ".join(
                f"{item['question']} {item['answer']}" for item in session["answers"]
            )
            session["query"] = joined_answers
            return session["query"]

        answers = session["answers"]
        prompt = f"""
                {TAVILY_QUERY_GENERATION_PROMPT}

                User answers:

                {answers}
                """.strip()

        response = self.llm.invoke(prompt)
        query = self.clean_single_line(response.content)
        session["query"] = query
        return session["query"]

    def extract_sources(self, product_results):
        sources = []
        for index, item in enumerate(product_results, start=1):
            title = item.get("title", "Lovehoney")
            url = item.get("url", "")
            if not url:
                continue
            score = item.get("score", "")
            sources.append(f"{index}. [{title}]({url}) \n score:{score}")
        return "\n".join(sources)

    def format_product_context(self, product_results):
        context_blocks = []
        for index, item in enumerate(product_results, start = 1):
            title = item.get("title", "untitled")
            url = item.get("url", "")
            #content = item.get("raw_content", "")[:MAX_CHARS_PER_PRODUCT]
            content = (item.get("content", ""))[:MAX_CHARS_PER_PRODUCT]
            context_blocks.append(
                f"{index}. {title}\n"
                f"URL: {url}\n"
                f"Content: {content}"
            )
        return "\n\n".join(context_blocks)    

    def build_recommendation_messages(self,session):
        user_prompt = f"""
                        Today is {TODAY}.

                        User preference summary:
                        {session.get("query","")}

                        Lovehoney product context:
                        {session.get("product_context", "")}
                       """.strip()
        return [SystemMessage(content=PRODUCT_RECOMMENDATION_PROMPT),
                HumanMessage(content=user_prompt)]

    def recommend_products(self,session):
        if not session.get("product_context", "").strip():
            return "I could not find enough Lovehoney product page context to recommend"
        messages = self.build_recommendation_messages(session)
        response = self.llm.invoke(messages)
        return response.content


#FINAL HANDLER

    def handle(self, user_message, session= None): # process the user's message inside the product discovery flow.
        if not self.is_active(session): #Handle missing, empty, or inactive sessions
            return self.start_survey(opening_message = user_message) # start a new discovery session instead of failing
        current_question = session.get("current_question") or self.generate_first_question(session)
        self.save_answer(session, current_question, user_message) # store user's answer update question counter
        answer_index = session["question_index"]  # Use the current answer number after save_answer increments it.
        session["answers"][-1]["answer_index"] = answer_index  # Store the step number on the latest answer.

        query = self.generate_search_query(session)  # Generate a concise Chroma query from all answers.
        all_results = self.search_for_question_context(query)  # Retrieve Chroma chunks.
        sources = self.extract_substep_sources(all_results, query, answer_index)  # Convert the pages into source objects.

        combined_summary = self.format_sources_for_combined_summary(sources)
        session["latest_sources_summary"] = combined_summary
        session["combined_sources_summaries"].append({
            "answer_index":answer_index,
            "query": query,
            "summary":combined_summary
        })  # Store summaries.

        session["last_all_results"] = all_results  # Store latest raw substep results.
        session["last_sources"] = sources  # Store the summarised substep sources.
        session["sources"].extend(sources)  # Store all substep sources for debugging.

        if session["question_index"] >= session["max_questions"]: #stop asking questions when the limit is reached.
            session["status"] = "summary_ready" # Mark the session as ready to proceed to the summary creation
            session["current_question"] = None
            summary = self.generate_tavily_search_query(session)
            all_product_results, product_results = self.search_products(summary)
            

            session["last_product_results"] = product_results
            session["product_context"] = self.format_product_context(product_results)
            session["status"] = "complete"
            answer = self.recommend_products(session)
            session["final_recommendation"] = answer
            #self.write_debug_markdown(session)

            return self.build_result(
                question=user_message,
                answer= answer,
                sources=(
                        "### Filtered product results\n"
                        f"{self.extract_sources(product_results)}"
                    ),
                session=session,
            )
        

        
        next_question = self.generate_next_question(session)  # Use latest summarized sources for grounded follow-up generation.
        session["current_question"] = next_question
        
        return self.build_result(
            question = user_message,
            answer = next_question,
            session = session,
        )



#DEBUGGING

    def format_debug_sources_for_answer(self, session, answer_index):
        related_sources = [
            source for source in session.get("sources", [])
            if source.get("answer_index") == answer_index
        ]

        if not related_sources:
            return "No Chroma sources stored for this answer."

        lines = []
        for index, source in enumerate(related_sources, start=1):
            lines.extend([
                f"{index}. {source.get('title', 'Untitled')}",
                f"   URL: {source.get('url', '')}",
                f"   Score: {source.get('score', '')}",
                "",
            ])

        return "\n".join(lines).strip()

    def format_debug_sources(self, results):
        lines = []

        for index, item in enumerate(results, start=1):
            title = item.get("title", "Untitled")
            url = item.get("url", "")
            lines.append(f"{index}. {title}\n   {url}")

        return "\n".join(lines)
    
    def find_combined_summary_for_answer(self, session, answer_index):
        for item in session.get("combined_sources_summaries", []):
            if item.get("answer_index") == answer_index:
                return item
        return {}

    def find_generated_question_after_answer(self, session, answer_index):
        answers = session.get("answers", [])

        for index, answer in enumerate(answers):
            if answer.get("answer_index") != answer_index:
                continue

            next_index = index + 1
            if next_index < len(answers):
                return answers[next_index].get("question", "")

            if session.get("status") == "complete":
                return "Survey complete. Final recommendation generated."

            return session.get("current_question") or ""

        return ""

    def write_debug_markdown(self, session):
        self.debug_dir.mkdir(parents=True, exist_ok=True)

        lines = [
            "# Tavily Product Discovery Debug Report",
            "",
            f"Generated at: {self.utc_timestamp()}",
            "",
            "## Survey Steps",
            "",
        ]

        for answer in session.get("answers", []):
            answer_index = answer.get("answer_index")
            summary_event = self.find_combined_summary_for_answer(session, answer_index)

            lines.extend([
                f"### Step {answer_index}",
                "",
                "#### User Answer",
                "",
                f"Question asked: {answer.get('question', '')}",
                "",
                f"User answered: {answer.get('answer', '')}",
                "",
                "#### Query Generated For Chroma",
                "",
                f"`{summary_event.get('query', '')}`",
                "",
                "#### Chroma Chunks Retrieved",
                "",
                self.format_debug_sources_for_answer(session, answer_index),
                "",
                "#### Combined Summary Used For Next Question",
                "",
                summary_event.get("summary", ""),
                "",
                "#### Generated Next Question",
                "",
                self.find_generated_question_after_answer(session, answer_index),
                "",
            ])

        lines.extend([
            "## Final Product Recommendation Generation",
            "",
            "### Final Tavily Query",
            "",
            f"`{session.get('query', '')}`",
            "",
            "### Filtered Product Results",
            "",
            self.extract_sources(session.get("last_product_results", [])) or "No filtered product results stored.",
            "",
            "### Product Context Sent To Recommendation LLM",
            "",
            "```text",
            session.get("product_context", ""),
            "```",
            "",
            "### Final Recommendation Text",
            "",
            session.get("final_recommendation", ""),
            "",
        ])

        self.debug_markdown_path.write_text("\n".join(lines), encoding="utf-8")
