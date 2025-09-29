/**
 * Crop Crystalline Chatbot - Frontend JavaScript
 */

class CropChatbot {
    constructor() {
        console.log('🌱 CropChatbot initializing...');
        this.sessionId = null;
        this.currentLanguage = 'auto';  // Always use auto-detection
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];

        console.log('Calling initializeElements...');
        this.initializeElements();
        console.log('Calling bindEvents...');
        this.bindEvents();
        console.log('Calling loadSupportedLanguages...');
        this.loadSupportedLanguages();
        console.log('Calling updateStatus...');
        this.updateStatus('Ready');
        console.log('✅ CropChatbot initialization complete');
    }

    initializeElements() {
        console.log('🔍 Finding DOM elements...');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.voiceBtn = document.getElementById('voice-btn');
        this.chatMessages = document.getElementById('chat-messages');
        this.languageSelect = document.getElementById('language-select');
        this.recordingIndicator = document.getElementById('recording-indicator');
        this.recordingText = document.getElementById('recording-text');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.responseAudio = document.getElementById('response-audio');
        this.statusDot = document.getElementById('status-dot');
        this.statusText = document.getElementById('status-text');

        // Check if critical elements exist
        const criticalElements = {
            'message-input': this.messageInput,
            'send-btn': this.sendBtn,
            'loading-overlay': this.loadingOverlay,
            'chat-messages': this.chatMessages
        };

        for (const [name, element] of Object.entries(criticalElements)) {
            if (!element) {
                console.error(`❌ Critical element missing: ${name}`);
            } else {
                console.log(`✅ Found element: ${name}`);
            }
        }

        // Hide loading overlay immediately if it exists
        if (this.loadingOverlay) {
            this.loadingOverlay.style.display = 'none';
            console.log('🚫 Loading overlay hidden on init');
        }
    }

    bindEvents() {
        // Send message events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Voice recording events
        this.voiceBtn.addEventListener('click', () => this.toggleRecording());
        this.recordingIndicator.addEventListener('click', () => this.stopRecording());

        // Language change event - always use auto-detection
        this.languageSelect.addEventListener('change', (e) => {
            this.currentLanguage = 'auto';  // Force auto-detection
            this.updateWelcomeMessage();
        });

        // Auto-resize text input
        this.messageInput.addEventListener('input', () => {
            this.updateSendButtonState();
        });

        this.updateSendButtonState();
    }

    updateSendButtonState() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText;
    }

    async loadSupportedLanguages() {
        try {
            const response = await fetch('/api/languages/');
            const data = await response.json();

            if (data.languages) {
                this.populateLanguageSelect(data.languages);
            }
        } catch (error) {
            console.error('Failed to load supported languages:', error);
        }
    }

    populateLanguageSelect(languages) {
        this.languageSelect.innerHTML = '';
        languages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.code;
            option.textContent = `${lang.native_name} (${lang.name})`;
            this.languageSelect.appendChild(option);
        });
        this.languageSelect.value = this.currentLanguage;
    }

    updateWelcomeMessage() {
        const welcomeMessages = {
                'en-US': {
                    greeting: "Hello! I'm your agricultural assistant. I can help you with:",
                    features: [
                        "🌾 Crop diseases and treatment",
                        "🐛 Pest identification and control",
                        "🧪 Fertilizer recommendations",
                        "🌤️ Weather-related farming advice",
                        "🌱 Soil health management"
                    ],
                    instruction: "You can type your question or use the microphone to speak!"
                },
                'es-ES': {
                    greeting: "¡Hola! Soy tu asistente agrícola. Puedo ayudarte con:",
                    features: [
                        "🌾 Enfermedades de cultivos y tratamiento",
                        "🐛 Identificación y control de plagas",
                        "🧪 Recomendaciones de fertilizantes",
                        "🌤️ Consejos agrícolas relacionados con el clima",
                        "🌱 Manejo de la salud del suelo"
                    ],
                    instruction: "¡Puedes escribir tu pregunta o usar el micrófono para hablar!"
                },
                'fr-FR': {
                    greeting: "Bonjour! Je suis votre assistant agricole. Je peux vous aider avec:",
                    features: [
                        "🌾 Maladies des cultures et traitement",
                        "🐛 Identification et contrôle des ravageurs",
                        "🧪 Recommandations d'engrais",
                        "🌤️ Conseils agricoles liés à la météo",
                        "🌱 Gestion de la santé des sols"
                    ],
                    instruction: "Vous pouvez taper votre question ou utiliser le microphone pour parler!"
                },
                'hi-IN': {
                    greeting: "नमस्ते! मैं आपका कृषि सहायक हूँ। मैं आपकी मदद कर सकता हूँ:",
                    features: [
                        "🌾 फसल रोग और उपचार",
                        "🐛 कीट पहचान और नियंत्रण",
                        "🧪 उर्वरक सिफारिशें",
                        "🌤️ मौसम संबंधी कृषि सलाह",
                        "🌱 मिट्टी स्वास्थ्य प्रबंधन"
                    ],
                    instruction: "आप अपना प्रश्न टाइप कर सकते हैं या बोलने के लिए माइक्रोफोन का उपयोग कर सकते हैं!"
                },
                'te-IN': {
                    greeting: "నమస్కారం! నేను మీ వ్యవసాయ సహాయకుడిని। నేను మీకు సహాయం చేయగలను:",
                    features: [
                        "🌾 పంట వ్యాధులు మరియు చికిత్స",
                        "🐛 కీటకాల గుర్తింపు మరియు నియంత్రణ",
                        "🧪 ఎరువుల సిఫార్సులు",
                        "🌤️ వాతావరణ సంబంధిత వ్యవసాయ సలహా",
                        "🌱 నేల ఆరోగ్య నిర్వహణ"
                    ],
                    instruction: "మీరు మీ ప్రశ్నను టైప్ చేయవచ్చు లేదా మాట్లాడటానికి మైక్రోఫోన్ ఉపయోగించవచ్చు!"
                },
                'pa-IN': {
                    greeting: "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡਾ ਖੇਤੀਬਾੜੀ ਸਹਾਇਕ ਹਾਂ। ਮੈਂ ਤੁਹਾਡੀ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ:",
                    features: [
                        "🌾 ਫਸਲਾਂ ਦੀਆਂ ਬਿਮਾਰੀਆਂ ਅਤੇ ਇਲਾਜ",
                        "🐛 ਕੀੜੇ-ਮਕੌੜਿਆਂ ਦੀ ਪਛਾਣ ਅਤੇ ਨਿਯੰਤਰਣ",
                        "🧪 ਖਾਦ ਦੀਆਂ ਸਿਫਾਰਸ਼ਾਂ",
                        "🌤️ ਮੌਸਮ ਸੰਬੰਧੀ ਖੇਤੀ ਸਲਾਹ",
                        "🌱 ਮਿੱਟੀ ਦੀ ਸਿਹਤ ਪ੍ਰਬੰਧਨ"
                    ],
                    instruction: "ਤੁਸੀਂ ਆਪਣਾ ਸਵਾਲ ਟਾਈਪ ਕਰ ਸਕਦੇ ਹੋ ਜਾਂ ਬੋਲਣ ਲਈ ਮਾਈਕ੍ਰੋਫੋਨ ਦੀ ਵਰਤੋਂ ਕਰ ਸਕਦੇ ਹੋ!"
                },
                'ta-IN': {
                    greeting: "வணக்கம்! நான் உங்கள் விவசாய உதவியாளர். நான் உங்களுக்கு உதவ முடியும்:",
                    features: [
                        "🌾 பயிர் நோய்கள் மற்றும் சிகிச்சை",
                        "🐛 பூச்சி அடையாளம் மற்றும் கட்டுப்பாடு",
                        "🧪 உர பரிந்துரைகள்",
                        "🌤️ வானிலை தொடர்பான விவசாய ஆலோசனை",
                        "🌱 மண் ஆரோக்கிய மேலாண்மை"
                    ],
                    instruction: "நீங்கள் உங்கள் கேள்வியை தட்டச்சு செய்யலாம் அல்லது பேச மைக்ரோஃபோனைப் பயன்படுத்தலாம்!"
                },
                'bn-IN': {
                    greeting: "নমস্কার! আমি আপনার কৃষি সহায়ক। আমি আপনাকে সাহায্য করতে পারি:",
                    features: [
                        "🌾 ফসলের রোগ এবং চিকিৎসা",
                        "🐛 পোকামাকড় চিহ্নিতকরণ এবং নিয়ন্ত্রণ",
                        "🧪 সার সুপারিশ",
                        "🌤️ আবহাওয়া সম্পর্কিত কৃষি পরামর্শ",
                        "🌱 মাটির স্বাস্থ্য ব্যবস্থাপনা"
                    ],
                    instruction: "আপনি আপনার প্রশ্ন টাইপ করতে পারেন বা কথা বলার জন্য মাইক্রোফোন ব্যবহার করতে পারেন!"
                },
                'mr-IN': {
                    greeting: "नमस्कार! मी तुमचा शेती सहाय्यक आहे। मी तुम्हाला मदत करू शकतो:",
                    features: [
                        "🌾 पिकांचे रोग आणि उपचार",
                        "🐛 कीटक ओळख आणि नियंत्रण",
                        "🧪 खत शिफारसी",
                        "🌤️ हवामान संबंधित शेती सल्ला",
                        "🌱 मातीचे आरोग्य व्यवस्थापन"
                    ],
                    instruction: "तुम्ही तुमचा प्रश्न टाईप करू शकता किंवा बोलण्यासाठी मायक्रोफोन वापरू शकता!"
                },
                'gu-IN': {
                    greeting: "નમસ્તે! હું તમારો કૃષિ સહાયક છું। હું તમારી મદદ કરી શકું છું:",
                    features: [
                        "🌾 પાકના રોગો અને સારવાર",
                        "🐛 જંતુ ઓળખ અને નિયંત્રણ",
                        "🧪 ખાતર ભલામણો",
                        "🌤️ હવામાન સંબંધિત કૃષિ સલાહ",
                        "🌱 માટીના આરોગ્ય વ્યવસ્થાપન"
                    ],
                    instruction: "તમે તમારો પ્રશ્ન ટાઈપ કરી શકો છો અથવા બોલવા માટે માઈક્રોફોનનો ઉપયોગ કરી શકો છો!"
                }
            };

        const messages = welcomeMessages[this.currentLanguage] || welcomeMessages['en-US'];
        const welcomeElement = document.querySelector('.welcome-message .message-content');

        if (welcomeElement) {
            welcomeElement.innerHTML = `
                <p>${messages.greeting}</p>
                <ul>
                    ${messages.features.map(feature => `<li>${feature}</li>`).join('')}
                </ul>
                <p>${messages.instruction}</p>
            `;
        }
    }
    
    async sendMessage() {
            const message = this.messageInput.value.trim();
            if (!message) return;

            // Clear input and disable send button
            this.messageInput.value = '';
            this.updateSendButtonState();

            // Add user message to chat
            this.addMessage('user', message);
            this.showLoading(true);
            this.updateStatus('Processing...');

            try {
                // Add timeout to prevent hanging requests
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

                const response = await fetch('/api/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: this.sessionId,
                        language_code: 'auto'  // Always use auto-detection
                    }),
                    signal: controller.signal
                });

                clearTimeout(timeoutId); // Clear timeout if request completes

                const data = await response.json();

                if (response.ok) {
                    this.sessionId = data.session_id;
                    this.addMessage('bot', data.response, {
                        intent: data.intent,
                        confidence: data.confidence,
                        responseTime: data.response_time
                    });
                    this.updateStatus('Ready');
                } else {
                    throw new Error(data.error || 'Failed to send message');
                }

            } catch (error) {
                console.error('Error sending message:', error);
                
                let errorMessage = 'Sorry, I encountered an error. Please try again.';
                if (error.name === 'AbortError') {
                    errorMessage = 'Request timed out. Please check your connection and try again.';
                    this.updateStatus('Timeout Error', 'error');
                } else if (error.message.includes('Failed to fetch')) {
                    errorMessage = 'Connection error. Please check if the server is running and try again.';
                    this.updateStatus('Connection Error', 'error');
                } else {
                    this.updateStatus('Error', 'error');
                }
                
                this.addMessage('bot', errorMessage, {
                    isError: true
                });
            } finally {
                // Ensure loading is always hidden, even if there's an error
                console.log('Finally block: hiding loading overlay');
                this.showLoading(false);
                this.hideLoading(); // Double-check to make sure it's hidden
            }
        }
    
    async toggleRecording() {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                await this.startRecording();
            }
        }
    
    async startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        sampleRate: 48000
                    }
                });

                // Check if browser supports SpeechRecognition for live transcription
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                    this.startLiveSpeechRecognition();
                } else {
                    // Fallback to original recording method
                    this.startTraditionalRecording(stream);
                }

            } catch (error) {
                console.error('Error starting recording:', error);
                alert('Could not access microphone. Please check permissions.');
                this.updateStatus('Microphone Error', 'error');
            }
        }

        startLiveSpeechRecognition() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();

            // Configure speech recognition for live transcription
            this.recognition.continuous = true;  // Keep listening
            this.recognition.interimResults = true;  // Show partial results

            // Set initial language - if auto, start with user's browser language or English
            if (this.currentLanguage === 'auto') {
                // Try to detect browser language first
                const browserLang = navigator.language || navigator.languages[0];
                const supportedLangs = ['en-US', 'hi-IN', 'ta-IN', 'te-IN', 'bn-IN', 'mr-IN', 'gu-IN', 'pa-IN', 'kn-IN', 'ml-IN'];
                this.recognition.lang = supportedLangs.includes(browserLang) ? browserLang : 'en-US';
            } else {
                this.recognition.lang = this.currentLanguage;
            }

            // Create live transcription message
            this.liveTranscriptionMessage = this.createLiveTranscriptionMessage();
            let finalTranscript = '';
            let interimTranscript = '';

            this.recognition.onresult = (event) => {
                interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }

                // Update live transcription display
                const fullText = finalTranscript + interimTranscript;
                this.updateLiveTranscription(fullText);

                // Update input field with final text
                if (finalTranscript.trim()) {
                    this.messageInput.value = finalTranscript.trim();
                    this.updateSendButtonState();

                    // Auto-detect language from transcribed text if in auto mode
                    if (this.currentLanguage === 'auto' && finalTranscript.trim()) {
                        this.detectAndUpdateLanguage(finalTranscript.trim());
                    }
                }
            };

            this.recognition.onstart = () => {
                this.isRecording = true;
                this.voiceBtn.classList.add('recording');
                this.recordingIndicator.style.display = 'flex';
                this.recordingText.textContent = 'Listening... (Live transcription)';
                this.updateStatus('Listening... (Live transcription)');
            };

            this.recognition.onend = () => {
                this.stopLiveRecording();
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopLiveRecording();
                if (event.error !== 'no-speech') {
                    this.updateStatus('Speech Error - try again', 'error');
                }
            };

            // Start recognition
            this.recognition.start();
        }

        startTraditionalRecording(stream) {
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.audioChunks = [];

            this.mediaRecorder.addEventListener('dataavailable', (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            });

            this.mediaRecorder.addEventListener('stop', () => {
                this.processRecording();
            });

            this.mediaRecorder.start();
            this.isRecording = true;
            this.voiceBtn.classList.add('recording');
            this.recordingIndicator.style.display = 'flex';
            this.updateStatus('Recording...');
        }

        stopRecording() {
            if (this.recognition) {
                // Stop live speech recognition
                this.recognition.stop();
            } else if (this.mediaRecorder && this.isRecording) {
                // Stop traditional recording
                this.mediaRecorder.stop();
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
        }

        stopLiveRecording() {
            this.isRecording = false;
            this.voiceBtn.classList.remove('recording');
            this.recordingIndicator.style.display = 'none';
            this.updateStatus('Text ready', 'ready');

            // Clean up live transcription message
            if (this.liveTranscriptionMessage && this.liveTranscriptionMessage.parentNode) {
                this.liveTranscriptionMessage.remove();
            }

            // Focus input for editing
            this.messageInput.focus();
        }

        createLiveTranscriptionMessage() {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user-message live-transcription';

            messageDiv.innerHTML = `
            <div class="avatar user-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">
                <small style="opacity: 0.7; color: #2196F3;">
                    <i class="fas fa-microphone"></i> Live transcription...
                </small>
                <p id="live-transcript-text" style="font-style: italic; opacity: 0.8;">
                    <span class="typing-indicator">Listening...</span>
                </p>
            </div>
        `;

            this.chatMessages.appendChild(messageDiv);
            this.scrollToBottom();

            return messageDiv;
        }

        updateLiveTranscription(text) {
            if (this.liveTranscriptionMessage) {
                const transcriptElement = this.liveTranscriptionMessage.querySelector('#live-transcript-text');
                if (transcriptElement) {
                    if (text.trim()) {
                        transcriptElement.textContent = text;
                    } else {
                        transcriptElement.innerHTML = '<span class="typing-indicator">Listening...</span>';
                    }
                    this.scrollToBottom();
                }
            }
        }

        detectAndUpdateLanguage(text) {
            // Simple language detection based on character patterns
            const detectedLang = this.detectLanguageFromText(text);

            if (detectedLang && detectedLang !== 'en-US') {
                // Update recording indicator to show detected language
                const languageNames = {
                    'hi-IN': 'हिन्दी',
                    'ta-IN': 'தமிழ்',
                    'te-IN': 'తెలుగు',
                    'bn-IN': 'বাংলা',
                    'mr-IN': 'मराठी',
                    'gu-IN': 'ગુજરાતી',
                    'pa-IN': 'ਪੰਜਾਬੀ',
                    'kn-IN': 'ಕನ್ನಡ',
                    'ml-IN': 'മലയാളം'
                };

                const langName = languageNames[detectedLang] || detectedLang;
                if (this.recordingText) {
                    this.recordingText.textContent = `Listening in ${langName}... (Live transcription)`;
                }
            }
        }

        detectLanguageFromText(text) {
            // Simple Unicode-based language detection
            if (!text) return 'en-US';

            // Telugu
            if (/[\u0C00-\u0C7F]/.test(text)) return 'te-IN';
            // Tamil  
            if (/[\u0B80-\u0BFF]/.test(text)) return 'ta-IN';
            // Hindi/Marathi (Devanagari)
            if (/[\u0900-\u097F]/.test(text)) {
                // Simple Marathi detection
                if (/काय|कसे|कुठे|कधी|शेती|पीक|खत/.test(text)) return 'mr-IN';
                return 'hi-IN';
            }
            // Bengali
            if (/[\u0980-\u09FF]/.test(text)) return 'bn-IN';
            // Gujarati
            if (/[\u0A80-\u0AFF]/.test(text)) return 'gu-IN';
            // Punjabi
            if (/[\u0A00-\u0A7F]/.test(text)) return 'pa-IN';
            // Kannada
            if (/[\u0C80-\u0CFF]/.test(text)) return 'kn-IN';
            // Malayalam
            if (/[\u0D00-\u0D7F]/.test(text)) return 'ml-IN';

            return 'en-US';
        }
    
    async processRecording() {
            if (this.audioChunks.length === 0) return;

            this.showLoading(true);
            this.updateStatus('Converting speech to text...');

            try {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm;codecs=opus' });
                const audioBase64 = await this.blobToBase64(audioBlob);

                // Use speech-to-text service to convert audio to text
                const speechResponse = await fetch('/api/speech-to-text/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        audio_data: audioBase64
                    })
                });

                const speechData = await speechResponse.json();

                if (speechResponse.ok && speechData.transcribed_text) {
                    // Set the transcribed text in the input field
                    this.messageInput.value = speechData.transcribed_text;
                    this.updateSendButtonState();

                    // Add transcribed message to show what was heard
                    this.addMessage('user', speechData.transcribed_text, {
                        isTranscribed: true,
                        showTranscribeNote: true
                    });

                    this.updateStatus('Text ready', 'Speech converted to text. Click Send or edit the text.');

                    // Auto-focus the input for editing if needed
                    this.messageInput.focus();

                } else {
                    throw new Error(speechData.error || 'Failed to transcribe speech');
                }

            } catch (error) {
                console.error('Error processing recording:', error);
                this.addMessage('bot', 'Sorry, I couldn\'t understand your speech. Please try again or type your question.', {
                    isError: true
                });
                this.updateStatus('Speech Error', 'error');
            } finally {
                this.showLoading(false);
            }
        }

        blobToBase64(blob) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => {
                    const base64 = reader.result.split(',')[1];
                    resolve(base64);
                };
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
        }

        playAudioResponse(audioBase64) {
            try {
                const audioBlob = this.base64ToBlob(audioBase64, 'audio/mp3');
                const audioUrl = URL.createObjectURL(audioBlob);
                this.responseAudio.src = audioUrl;
                this.responseAudio.play();

                // Clean up URL after playing
                this.responseAudio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                };
            } catch (error) {
                console.error('Error playing audio response:', error);
            }
        }

        base64ToBlob(base64, mimeType) {
            const byteCharacters = atob(base64);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            return new Blob([byteArray], { type: mimeType });
        }

        addMessage(type, content, metadata = {}) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';

            const isUser = type === 'user';
            const avatarIcon = isUser ? 'fas fa-user' : 'fas fa-robot';
            const messageClass = isUser ? 'user-message' : 'bot-message';
            const avatarClass = isUser ? 'user-avatar' : 'bot-avatar';

            messageDiv.classList.add(messageClass);

            let audioControls = '';
            if (metadata.audioResponse && !isUser) {
                audioControls = `
                <div class="audio-controls">
                    <button class="audio-btn" onclick="this.parentElement.parentElement.querySelector('audio').play()" title="Play audio">
                        <i class="fas fa-play"></i>
                    </button>
                    <audio preload="none">
                        <source src="data:audio/mp3;base64,${metadata.audioResponse}" type="audio/mp3">
                    </audio>
                </div>
            `;
            }

            let transcribedIndicator = '';
            if (metadata.isTranscribed) {
                if (metadata.showTranscribeNote) {
                    transcribedIndicator = '<small style="opacity: 0.7; color: #2196F3;"><i class="fas fa-microphone"></i> Speech-to-text conversion</small><br>';
                } else {
                    transcribedIndicator = '<small style="opacity: 0.7;"><i class="fas fa-microphone"></i> Voice input</small><br>';
                }
            }

            let errorIndicator = '';
            if (metadata.isError) {
                errorIndicator = '<small style="color: #f44336;"><i class="fas fa-exclamation-triangle"></i> Error</small><br>';
            }

            messageDiv.innerHTML = `
            <div class="avatar ${avatarClass}">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-content">
                ${transcribedIndicator}
                ${errorIndicator}
                <p>${this.formatMessage(content)}</p>
                ${audioControls}
            </div>
        `;

            this.chatMessages.appendChild(messageDiv);
            this.scrollToBottom();
        }

        formatMessage(content) {
            // Simple formatting for better readability
            return content
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>');
        }

        scrollToBottom() {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }

        showLoading(show) {
            console.log('showLoading called with:', show);
            if (this.loadingOverlay) {
                if (show) {
                    this.loadingOverlay.classList.add('active');
                } else {
                    this.loadingOverlay.classList.remove('active');
                }
                console.log('Loading overlay active class:', this.loadingOverlay.classList.contains('active'));
            } else {
                console.error('Loading overlay element not found!');
            }
        }

        hideLoading() {
            console.log('hideLoading called');
            this.showLoading(false);
        }

        updateStatus(text, type = 'ready') {
            this.statusText.textContent = text;
            this.statusDot.className = `status-dot ${type}`;
        }
    }

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CropChatbot();
});

// Service worker registration for offline support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}