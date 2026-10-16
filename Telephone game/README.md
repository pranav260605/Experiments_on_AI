# ☎️ Telephone Game — How Meaning Changes Across AI Models

> **An experiment in how information changes when the same prompt travels through different AI models.**

## 🧠 What is this experiment?

The **Telephone Game** explores a simple question:

> **If we pass the same piece of information through multiple AI models, how much does the meaning change?**

The idea is similar to the childhood telephone game.

One person says something.

It gets repeated.

Then repeated again.

And after several rounds, the final message may look similar to the original — but the meaning can subtly change.

I wanted to see whether the same thing happens when information is passed between LLMs.

---

## 🎯 The Experiment

The experiment takes an original statement and passes it through multiple AI models.

```text
Original Information
        ↓
     Claude
        ↓
     ChatGPT
        ↓
      Gemini
        ↓
     Claude
        ↓
     ChatGPT
        ↓
   Final Output
```

At every stage, the model receives information produced by the previous model.

The goal is **not simply to measure which model is "best."**

Instead, the goal is to observe:

- What information is preserved?
- What information disappears?
- What new assumptions appear?
- Does the model become more confident while becoming less accurate?
- How does wording change the interpretation?
- Where does the original meaning get distorted?

---

## 🔬 Example

One of the experiments looked at a SQL concept involving a `LEFT JOIN`.

The original meaning was essentially:

> Only rows where a match exists in both tables.

As the statement travelled through different models, the wording changed.

Some models preserved the intended meaning.

Others gradually introduced a different interpretation.

This is the interesting part of the experiment:

### Similar wording ≠ identical meaning

A response can **sound very similar to the original** while actually changing an important logical condition.

---

## 🖼️ Visualization

![Telephone Game experiment visualization](./assets/telephone-game.png)

The visualization shows how the information changes as it passes through different AI models.

---

## 💡 The Key Insight

The experiment made me interested in a broader question:

> **Can AI systems preserve meaning reliably when information is repeatedly transformed?**

This matters because AI systems increasingly communicate with:

- other AI agents
- automated pipelines
- summarization systems
- retrieval systems
- evaluation systems
- human users

A small semantic change at one stage can become a significant error after several transformations.

---

## 🧪 What I am measuring

The experiment can be extended to compare models on:

| Dimension | Question |
|---|---|
| Semantic preservation | Did the original meaning survive? |
| Accuracy | Is the final statement factually correct? |
| Logical consistency | Did logical relationships change? |
| Confidence | Did the model become more confident despite changing the meaning? |
| Information loss | What details disappeared? |
| Information addition | Did the model introduce unsupported details? |
| Error propagation | Do small errors become larger over multiple rounds? |

---

## 🚀 Why this experiment is interesting

This is not intended to be another chatbot application.

The interesting question is the **behavior of AI systems themselves**.

Instead of asking:

> "Can I build something with an LLM?"

the experiment asks:

> **"What happens when LLMs are used as components in a chain?"**

That distinction is what makes this an experiment rather than simply an AI application.

---

## 📁 Repository Structure

```text
Telephone game/
│
├── README.md
├── outputs.txt
│
└── assets/
    └── telephone-game.png
```

---

## 🔭 Possible Extensions

Future experiments could test:

1. **More models**  
   Compare additional LLMs in the chain.

2. **Longer chains**  
   Test 5, 10, 20 or 50 rounds.

3. **Different types of information**  
   - SQL
   - mathematics
   - legal text
   - technical documentation
   - instructions
   - factual statements

4. **Automatic semantic evaluation**  
   Use another model or human evaluation to measure how much the meaning changed.

5. **Error propagation**  
   Identify the round where the first meaningful deviation occurs.

6. **Prompt sensitivity**  
   Test whether different system prompts change how information survives.

---

## 🧩 Core Question

The entire project can be reduced to one question:

> **When information travels through AI, does the message survive — or does it slowly become a different message?**

---

## 📜 Status

**Experiment / Research Prototype**

This repository contains the outputs and observations from the experiment.
