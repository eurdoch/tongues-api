import express from 'express';
import axios from 'axios';
import { PollyClient, SynthesizeSpeechCommand } from "@aws-sdk/client-polly";

const app = express();
app.use(express.json());

const config = {
  AWS_REGION: process.env.AWS_REGION || "us-east-1",
  AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY,
  MODEL_ID: "anthropic.claude-3-5-sonnet-20240620-v1:0",
};

const pollyClient = new PollyClient({
  region: config.AWS_REGION, 
  credentials: {
    accessKeyId: config.AWS_ACCESS_KEY_ID,
    secretAccessKey: config.AWS_SECRET_ACCESS_KEY,
  }
});

const LANGUAGE_TO_VOICE = {
  'French': 'Mathieu',
  'Dutch': 'Ruben',
  'English': 'Matthew',
  'German': 'Hans',
  'Spanish': 'Enrique',
  'Italian': 'Giorgio',
  'Japanese': 'Takumi',
  'Portuguese': 'Cristiano',
  'Chinese': 'Zhiwei'
};

app.get('/ping', (req, res) => {
  console.log('Received /ping request');
  res.status(200).send('pong');
});

app.post('/translate', async (req, res) => {
  console.log('Received /translate request');
  const { language, text } = req.body;
  const anthropicApiKey = process.env.ANTHROPIC_API_KEY;

  if (!anthropicApiKey) {
    res.status(500).send('ANTHROPIC_API_KEY must be set');
    return;
  }

  const prompt = `Translate the following text from source language to target language. Only return the translated text.

Source language: ${language}
Target language: English
Text: ${text}
`;

  try {
    const response = await axios.post('https://api.anthropic.com/v1/messages', {
      model: 'claude-3-haiku-20240307',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    }, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': anthropicApiKey,
        'anthropic-version': '2023-06-01'
      }
    });

    const translatedText = response.data.content[0].text;
    res.status(200).json({ translated_text: translatedText });
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

app.post('/speech', async (req, res) => {
  console.log('Received /speech request');
  const { language, text } = req.body;
  const voiceId = LANGUAGE_TO_VOICE[language];

  if (!voiceId) {
    res.status(400).send('Invalid language');
    return;
  }

  try {
    const command = new SynthesizeSpeechCommand({
      Text: text,
      OutputFormat: "mp3", // Can be "mp3", "ogg_vorbis", or "pcm"
      VoiceId: voiceId,
    });

    const response = await pollyClient.send(command);

    if (response.AudioStream) {
      const audioBuffer = await response.AudioStream.transformToByteArray();
      console.log('Speech synthesis successful');
      res.status(200);
      res.set({
        'Content-Type': 'audio/mpeg',
        'Content-Length': audioBuffer.length
      });

    res.send(Buffer.from(audioBuffer));
    } else {
      res.status(500).send('Failed to generate speech');
    }
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

app.post('/language', async (req, res) => {
  console.log('Received /language request');
  const { text } = req.body;
  const anthropicApiKey = process.env.ANTHROPIC_API_KEY;

  if (!anthropicApiKey) {
    res.status(500).send('ANTHROPIC_API_KEY must be set');
    return;
  }

  const prompt = `
Format your response as JSON with field language.

Return the language of the text in the style of { language: "Spanish" }. 

Text: ${text}
`;

  try {
    const response = await axios.post('https://api.anthropic.com/v1/messages', {
      model: 'claude-3-haiku-20240307',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    }, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': anthropicApiKey,
        'anthropic-version': '2023-06-01'
      }
    });

    // TODO if parse fails retry query
    const language = response.data.content[0].text;
    const parsed = JSON.parse(language);
    res.status(200).json(parsed);
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

app.post('/verb-tenses', async (req, res) => {
  console.log('Received /verb-tenses request');
  const { verb } = req.body;
  const anthropicApiKey = process.env.ANTHROPIC_API_KEY;

  if (!anthropicApiKey) {
    res.status(500).send('ANTHROPIC_API_KEY must be set');
    return;
  }

  const prompt = `
Return all tenses and conjugations of the verb ${verb}, including the infinitive and affirmative along with translation in English.
`;

  try {
    const response = await axios.post('https://api.anthropic.com/v1/messages', {
      model: 'claude-3-haiku-20240307',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    }, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': anthropicApiKey,
        'anthropic-version': '2023-06-01'
      }
    });

    const verbTenses = response.data.content[0].text;
    const jsonResponse = {
      message: verbTenses,
    }
    res.status(200).json(jsonResponse);
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

app.post('/marks', async (req, res) => {
  console.log('Received /marks request');
  const { language, text } = req.body;
  console.log('Language: ', language);
  console.log('Text', text);
  const voiceId = LANGUAGE_TO_VOICE[language];

  if (!voiceId) {
    res.status(400).send('Invalid language');
    return;
  }

  try {
    const command = new SynthesizeSpeechCommand({
      Text: text,
      OutputFormat: "json",
      VoiceId: voiceId,
      SpeechMarkTypes: ["word"]
    });

    const response = await pollyClient.send(command);

    if (response.AudioStream) {
      const chunks = [];
      for await (const chunk of response.AudioStream) {
        chunks.push(chunk);
      }
      
      const buffer = Buffer.concat(chunks);
      const markData = buffer.toString('utf8');
      
      // Parse each line as JSON objects and return as array
      const marks = markData.trim().split('\n').map(line => JSON.parse(line));
      
      console.log('Speech marks generated successfully');
      res.status(200).json({ marks });
    } else {
      res.status(500).send('Failed to generate speech marks');
    }
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

app.post('/explain', async (req, res) => {
  console.log('Received /explain request');
  const { word, language } = req.body;
  const anthropicApiKey = process.env.ANTHROPIC_API_KEY;

  if (!anthropicApiKey) {
    res.status(500).send('ANTHROPIC_API_KEY must be set');
    return;
  }

  const prompt = `
Explain the meaning of the following word in English. Provide a clear and concise explanation suitable for language learners.

Language: ${language}
Word: ${word}
`;

  try {
    const response = await axios.post('https://api.anthropic.com/v1/messages', {
      model: 'claude-3-haiku-20240307',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    }, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': anthropicApiKey,
        'anthropic-version': '2023-06-01'
      }
    });

    const explanation = response.data.content[0].text;
    res.status(200).json({ explanation });
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

app.listen(3002, () => {
  console.log('Server listening on port 3002');
});

