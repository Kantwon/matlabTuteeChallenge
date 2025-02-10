# 🎈 Streamlit + LLM Examples App

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)
[![Open in StackBlitz](https://developer.stackblitz.com/img/open_in_stackblitz.svg)](https://stackblitz.com/github/Kantwon/matlabTuteeChallenge)
[![Open with CodeSandbox](https://assets.codesandbox.io/github/button-edit-lime.svg)](https://codesandbox.io/p/sandbox/github/Kantwon/matlabTuteeChallenge)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Kantwon/matlabTuteeChallenge)
[![Open in Codeanywhere](https://codeanywhere.com/img/open-in-codeanywhere-btn.svg)](https://app.codeanywhere.com/#https://github.com/Kantwon/matlabTuteeChallenge)

Starter examples for building LLM apps with Streamlit.

## Overview of the App

This app showcases a growing collection of LLM minimum working examples.

Current examples include:

- Chatbot
- File Q&A
- Chat with Internet search
- LangChain Quickstart
- LangChain PromptTemplate
- Chat with user feedback

## Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://llm-examples.streamlit.app/)

### Get an OpenAI API key

You can get your own OpenAI API key by following the following instructions:

1. Go to https://platform.openai.com/account/api-keys.
2. Click on the `+ Create new secret key` button.
3. Next, enter an identifier name (optional) and click on the `Create secret key` button.

### Enter the OpenAI API key in Streamlit Community Cloud

To set the OpenAI API key as an environment variable in Streamlit apps, do the following:

1. At the lower right corner, click on `< Manage app` then click on the vertical "..." followed by clicking on `Settings`.
2. This brings the **App settings**, next click on the `Secrets` tab and paste the API key into the text box as follows:

```sh
OPENAI_API_KEY='xxxxxxxxxx'
```

## Run it locally

```sh
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run Chatbot.py
```
