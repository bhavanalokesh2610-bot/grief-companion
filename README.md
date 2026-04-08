🌿 Grief Companion AI

An AI-powered multi-agent system designed to provide emotional support, journaling, and wellness guidance for users experiencing grief and difficult emotions.

---

🚀 Features

🤖 **Multi-Agent System**

  * Conversation Agent (empathetic support)
  * Journal Agent (store and retrieve reflections)
  * Wellness Agent (coping techniques & mood tracking)
  * Routine Agent (daily structure suggestions)

🧠 **Emotion-Aware Responses**

  * Understands user feelings
  * Suggests personalized coping strategies

📓 **Journaling System**

  * Save and retrieve reflections

💬 **Chat API**

  * Built using FastAPI
  * Supports real-time interaction

---

🏗️ Tech Stack

* Python
* Google ADK (Agent Development Kit)
* Gemini API
* FastAPI
* Cloud Run (Deployment)

---

⚙️ How It Works

1. User sends a message
2. Root agent understands intent
3. Delegates to appropriate sub-agent
4. Agent processes request and responds

---

🗂️ Project Structure

* `agent.py` → Main application with all agents
* API endpoints:

  * `/chat` → Chat with AI
  * `/history/journal` → View journal entries
  * `/history/mood` → View mood logs

<img width="958" height="438" alt="image" src="https://github.com/user-attachments/assets/05cb4e52-1fe1-4527-b75e-cd394812b526" />

---

📦 Data Handling

Currently uses **in-memory storage** for:

* Journal entries
* Mood tracking

👉 Can be extended to use **Firestore / Database** for persistence.

---

🌐 Deployment

Deployed using Google Cloud Run.

---

🎯 Future Improvements

* Add Firestore database
* User authentication
* Mobile app integration
* Advanced emotion detection

---

Author

Bhavana L

---

💡 Note

This project is a prototype focused on demonstrating multi-agent coordination and emotional AI systems.
