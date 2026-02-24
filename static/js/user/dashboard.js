document.addEventListener("DOMContentLoaded", async function () {

    const logoutBtn = document.getElementById("logoutBtn");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", function () {
            localStorage.removeItem("token");
            window.location.href = "/auth/login";
        });
    }

    loadSaldo();
    loadHistory();
});

async function loadSaldo() {
    try {
        const data = await API.get("/wallet/me");

        if (data.balance !== undefined) {
            document.getElementById("saldoAmount").innerText =
                formatRupiah(data.balance);
        }
    } catch (err) {
        console.log("Error load saldo");
    }
}

async function loadHistory() {
    try {
        const data = await API.get("/orders/me");

        const container = document.querySelector(".transaction-section");
        container.innerHTML = "<h3>Transaksi Terbaru</h3>";

        data.forEach(order => {
            const div = document.createElement("div");
            div.className = "transaction-item";
            div.innerHTML = `
                <div>
                    <strong>Order #${order.id}</strong>
                    <p>${order.target}</p>
                </div>
                <span class="negative">- Rp ${order.amount || 0}</span>
            `;
            container.appendChild(div);
        });

    } catch (err) {
        console.log("Error load history");
    }
}

function formatRupiah(number) {
    return "Rp " + Number(number).toLocaleString("id-ID");
}