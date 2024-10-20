use std::collections::HashMap;

use aws_config::BehaviorVersion;
use axum::{http::{Method, StatusCode}, routing::{get, post}, Json, Router};
use lazy_static::lazy_static;
use serde::{Deserialize, Serialize};
use aws_sdk_polly::{types::OutputFormat, Client};
use aws_sdk_polly::types::VoiceId;
use tower_http::cors::{CorsLayer, Any};

lazy_static! {
    static ref LANGUAGE_TO_VOICE: std::collections::HashMap<&'static str, &'static str> = {
        let mut m = HashMap::new();
        m.insert("French", "Mathieu");
        m.insert("English", "Matthew");
        m.insert("German", "Hans");
        m.insert("Spanish", "Enrique");
        m.insert("Italian", "Giorgio");
        m.insert("Japanese", "Takumi");
        m.insert("Portuguese", "Cristiano");
        m.insert("Chinese", "Zhiwei");
        m
    };
}

#[derive(Serialize, Deserialize)]
struct TranslateRequest {
    language: String,
    text: String,
}

#[derive(Serialize, Deserialize)]
struct TranslateResponse {
    translated_text: String,
}

#[derive(Serialize, Deserialize)]
struct SpeechRequest {
    language: String,
    text: String,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let cors = CorsLayer::new()
        // allow `GET` and `POST` when accessing the resource
        .allow_methods([Method::GET, Method::POST])
        // allow requests from any origin
        .allow_origin(Any)
        // allow all headers
        .allow_headers(Any);

    let app = Router::new()
        .route("/", get(root))
        .route("/translate", post(translate))
        .route("/speech", post(speech))
        .layer(cors);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn root() -> &'static str {
    "Hello, World!"
}

async fn translate(Json(payload): Json<TranslateRequest>) -> Json<TranslateResponse> {
    let client = reqwest::Client::new();
    let anthropic_api_key = std::env::var("ANTHROPIC_API_KEY").expect("ANTHROPIC_API_KEY must be set");

    let prompt = format!("Translate the following text from source language to target language. Only return the translated text.

Source language: {}
Target language: English
Text: {}
", payload.language, payload.text);

    let response = client
        .post("https://api.anthropic.com/v1/messages")
        .header("Content-Type", "application/json")
        .header("X-API-Key", anthropic_api_key)
        .header("anthropic-version", "2023-06-01")
        .json(&serde_json::json!({
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }))
        .send()
        .await
        .expect("Failed to send request to Anthropic API");

    let response_body: serde_json::Value = response.json().await.expect("Failed to parse Anthropic API response");
    let translated_text = response_body["content"][0]["text"]
        .as_str()
        .unwrap_or("Translation failed")
        .to_string();

    Json(TranslateResponse { translated_text })
}

async fn speech(Json(payload): Json<SpeechRequest>) -> Result<Vec<u8>, StatusCode> {
    let config = aws_config::load_defaults(BehaviorVersion::v2024_03_28()).await;
    let client = Client::new(&config);

    let voice_id_str = LANGUAGE_TO_VOICE.get(payload.language.as_str())
        .ok_or(StatusCode::BAD_REQUEST)?;
    let voice_id = VoiceId::from(*voice_id_str);

    let output = client
        .synthesize_speech()
        .output_format(OutputFormat::Mp3)
        .text(payload.text)
        .voice_id(voice_id)
        .send()
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let audio_stream = output.audio_stream.collect().await.unwrap();
    Ok(audio_stream.into_bytes().to_vec())
}


