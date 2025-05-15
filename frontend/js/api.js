// api.js - Arquivo para lidar com as chamadas de API

const API_BASE_URL = window.location.protocol + '//' + window.location.hostname + ':5000/api';

// Função auxiliar para fazer requisições
async function fetchAPI(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include' // Incluir cookies para autenticação
    };

    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const responseData = await response.json();

        if (!response.ok) {
            throw new Error(responseData.error || 'Ocorreu um erro na requisição');
        }

        return responseData;
    } catch (error) {
        console.error('Erro na API:', error);
        throw error;
    }
}

// Função específica para upload de arquivo
async function uploadFile(endpoint, file, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);

    // Adicionar dados extras, se houver
    Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
    });

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData,
            credentials: 'include' // Incluir cookies para autenticação
        });

        const responseData = await response.json();

        if (!response.ok) {
            throw new Error(responseData.error || 'Ocorreu um erro no upload');
        }

        return responseData;
    } catch (error) {
        console.error('Erro no upload:', error);
        throw error;
    }
}

// API de autenticação
const authAPI = {
    register: (userData) => fetchAPI('/register', 'POST', userData),
    login: (credentials) => fetchAPI('/login', 'POST', credentials),
    logout: () => fetchAPI('/logout', 'POST'),
    getCurrentUser: () => fetchAPI('/user')
};

// API de portfólio
const portfolioAPI = {
    // Upload de portfólio
    uploadPortfolio: (file) => uploadFile('/upload-portfolio', file),
    
    // Obter resumo do portfólio com parâmetros de data
    getSummary: (startDate, endDate) => {
        const params = new URLSearchParams();
        
        if (startDate) {
            // Validar o formato da data antes de enviar
            if (/^\d{4}-\d{2}-\d{2}$/.test(startDate)) {
                params.append('start_date', startDate);
            } else {
                console.error('Formato de data inicial inválido. Use YYYY-MM-DD');
            }
        }
        
        if (endDate) {
            // Validar o formato da data antes de enviar
            if (/^\d{4}-\d{2}-\d{2}$/.test(endDate)) {
                params.append('end_date', endDate);
            } else {
                console.error('Formato de data final inválido. Use YYYY-MM-DD');
            }
        }
        
        const endpoint = `/portfolio-summary${params.toString() ? `?${params.toString()}` : ''}`;
        return fetchAPI(endpoint);
    },
    
    // Obter distribuição do portfólio
    getDistribution: () => fetchAPI('/portfolio-distribution'),      // Download de template
    downloadTemplate: (format = 'xlsx') => {
        // Link direto para o arquivo template no Google Drive
        const googleDriveTemplateUrl = 'https://drive.google.com/uc?export=download&id=1W3GI8bGTNxyMdgJ05qEhPUUE_MW1AJFU';
        
        // Usa o Google Drive diretamente para maior confiabilidade
        window.open(googleDriveTemplateUrl);
        return Promise.resolve({ message: 'Download iniciado' });
    },    // Adiciona função para registrar aportes
    registerAporte: (data) => fetchAPI('/register-aporte', 'POST', data),
    
    // Atualização manual por empresa
    updateEmpresa: (data) => fetchAPI('/empresa-update', 'POST', data)
};

// API de utilitários
const utilsAPI = {
    getExchangeRate: () => fetchAPI('/exchange-rate'),
    healthCheck: () => fetchAPI('/health'),
    getSystemStatus: () => fetchAPI('/system-status')
};

// API de dividendos
const dividendAPI = {
    // Obter dividendos do usuário
    getDividends: () => fetchAPI('/dividends'),
    
    // Atualizar status de recebimento de dividendos
    updateReceiptStatus: (data) => fetchAPI('/dividend-receipt', 'POST', data),
    
    // Obter status de recebimento de dividendos
    getReceiptStatus: () => fetchAPI('/dividend-receipt')
};

// Exportar as APIs
export { authAPI, portfolioAPI, utilsAPI, dividendAPI };