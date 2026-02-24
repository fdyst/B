const API = {
    getToken() {
        return localStorage.getItem("token");
    },

    async request(url, method = "GET", body = null) {
        const options = {
            method: method,
            headers: {
                "Content-Type": "application/json",
            }
        };

        const token = this.getToken();
        if (token) {
            options.headers["Authorization"] = `Bearer ${token}`;
        }

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);

        if (response.status === 401) {
            localStorage.removeItem("token");
            window.location.href = "/auth/login";
        }

        return response.json();
    },

    get(url) {
        return this.request(url, "GET");
    },

    post(url, body) {
        return this.request(url, "POST", body);
    }
};