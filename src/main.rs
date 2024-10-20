use axum::{
    routing::{get, post},
    http::StatusCode,
    Json, Router,
};
use serde::{Deserialize, Serialize};
use axum_test::TestServer;

#[derive(Serialize, Deserialize)]
struct TranslateRequest {
    language: String,
    text: String,
}

#[derive(Serialize, Deserialize)]
struct TranslateResponse {
    translated_text: String,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let app = Router::new()
        .route("/", get(root))
        .route("/translate", post(translate));

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

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_root() {
        let app = Router::new().route("/", get(root));
        let server = TestServer::new(app).unwrap();

        let response = server.get("/").await;
        assert_eq!(response.status_code(), StatusCode::OK);
        assert_eq!(response.text(), "Hello, World!");
    }

    #[tokio::test]
    async fn test_translate() {
        let app = Router::new().route("/translate", post(translate));
        let server = TestServer::new(app).unwrap();

        let payload = TranslateRequest {
            language: "en".to_string(),
            text: "Hello".to_string(),
        };

        let response = server
            .post("/translate")
            .json(&payload)
            .await;

        assert_eq!(response.status_code(), StatusCode::OK);

        let body: TranslateResponse = response.json();
        assert_eq!(body.translated_text, "Hello");
    }
}
