const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

/**
 * Upload a document to Paperless-ngx
 * @param {string} filePath - Path to the document file
 * @param {string} apiUrl - Paperless-ngx API URL
 * @param {string} apiToken - Paperless-ngx API token
 * @param {string} filename - Optional filename for the document
 * @returns {Promise<{success: boolean, statusCode: number|null, response: any}>}
 */
async function uploadToPaperless(filePath, apiUrl, apiToken, filename = null) {
    try {
        const form = new FormData();
        form.append('document', fs.createReadStream(filePath));

        // Add title if filename is provided
        if (filename) {
            const title = path.parse(filename).name; // Remove extension
            form.append('title', title);
        }

        const response = await axios.post(
            `${apiUrl}/api/documents/post_document/`,
            form,
            {
                headers: {
                    'Authorization': `Token ${apiToken}`,
                    ...form.getHeaders()
                }
            }
        );

        console.log('Upload successful:', response.data);
        return {
            success: true,
            statusCode: response.status,
            response: response.data
        };

    } catch (error) {
        console.error('Upload failed:', error.response?.status, error.response?.data);
        return {
            success: false,
            statusCode: error.response?.status || null,
            response: error.response?.data || error.message
        };
    }
}

module.exports = {
    uploadToPaperless
};
