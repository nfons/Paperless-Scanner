const OpenAI = require('openai');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const fs = require('fs').promises;
const sharp = require('sharp');

/**
 * Convert image file to base64
 * @param {string} filePath - Path to image file
 * @returns {Promise<string>} Base64 encoded image
 */
async function imageToBase64(filePath) {
    const buffer = await fs.readFile(filePath);
    return buffer.toString('base64');
}

/**
 * Clean and format filename
 * @param {string} filename - Raw filename from AI
 * @returns {string} Cleaned filename
 */
function cleanFilename(filename) {
    // Remove quotes and extra spaces
    let cleaned = filename.replace(/["']/g, '').trim();

    // Replace spaces with underscores
    cleaned = cleaned.replace(/ /g, '_');

    // Remove invalid characters
    cleaned = cleaned.replace(/[^a-zA-Z0-9_-]/g, '');

    // Ensure reasonable length
    if (cleaned.length > 50) {
        cleaned = cleaned.substring(0, 50);
    }

    return cleaned || 'document';
}

/**
 * Get recommended filename using OpenAI GPT-4o-mini
 * @param {string} imagePath - Path to the image file
 * @param {string} apiKey - OpenAI API key
 * @returns {Promise<string>} Recommended filename (without extension)
 */
async function getRecommendedFilenameOpenAI(imagePath, apiKey) {
    try {
        const openai = new OpenAI({ apiKey });
        const base64Image = await imageToBase64(imagePath);

        const response = await openai.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: [
                {
                    role: 'system',
                    content: 'You are a helpful assistant that analyzes documents and suggests appropriate filenames. Generate a concise, descriptive filename (without extension) based on the document content. Focus on the main subject, document type, and key identifiers. Use underscores instead of spaces and keep it under 50 characters.'
                },
                {
                    role: 'user',
                    content: [
                        {
                            type: 'text',
                            text: 'Analyze this document and suggest a filename (without extension) that describes its content. Return only the filename, nothing else.'
                        },
                        {
                            type: 'image_url',
                            image_url: {
                                url: `data:image/jpeg;base64,${base64Image}`
                            }
                        }
                    ]
                }
            ],
            max_tokens: 50,
            temperature: 0.3
        });

        const recommendedFilename = response.choices[0].message.content.trim();
        return cleanFilename(recommendedFilename);

    } catch (error) {
        console.error('Error getting OpenAI filename recommendation:', error);
        return '';
    }
}

/**
 * Get recommended filename using Google Gemini
 * @param {string} imagePath - Path to the image file
 * @param {string} apiKey - Gemini API key
 * @returns {Promise<string>} Recommended filename (without extension)
 */
async function getRecommendedFilenameGemini(imagePath, apiKey) {
    try {
        const genAI = new GoogleGenerativeAI(apiKey);
        const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

        // Read image file
        const imageBuffer = await fs.readFile(imagePath);
        const base64Image = imageBuffer.toString('base64');

        const prompt = 'Analyze this document and suggest a filename (without extension) that describes its content. Return only the filename, nothing else. Use underscores instead of spaces and keep it under 25 characters.';

        const result = await model.generateContent([
            prompt,
            {
                inlineData: {
                    mimeType: 'image/jpeg',
                    data: base64Image
                }
            }
        ]);

        const response = await result.response;
        const recommendedFilename = response.text().trim();
        return cleanFilename(recommendedFilename);

    } catch (error) {
        console.error('Error getting Gemini filename recommendation:', error);
        return '';
    }
}

/**
 * Get recommended filename based on available API key
 * @param {string} imagePath - Path to the image file
 * @param {Object} config - Configuration object with API keys
 * @returns {Promise<string>} Recommended filename (without extension)
 */
async function getRecommendedFilename(imagePath, config) {
    if (config.openai_api_key) {
        return await getRecommendedFilenameOpenAI(imagePath, config.openai_api_key);
    } else if (config.gemini_api_key) {
        return await getRecommendedFilenameGemini(imagePath, config.gemini_api_key);
    } else {
        return '';
    }
}

module.exports = {
    getRecommendedFilename,
    getRecommendedFilenameOpenAI,
    getRecommendedFilenameGemini
};
