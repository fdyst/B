const API_CATEGORIES = "/categories";

async function loadCategories() {
    const res = await fetch(API_CATEGORIES + "/");
    const data = await res.json();

    const container = document.getElementById("categoryList");
    container.innerHTML = "";

    if (!data.length) {
        container.innerHTML = "<p>Tidak ada kategori</p>";
        return;
    }

    data.forEach(c => {
        container.innerHTML += `
            <div class="card">
                <strong>${c.name}</strong>
                <div class="status">
                    Status: ${c.is_active ? "🟢 Aktif" : "🔴 Nonaktif"}
                </div>

                <button class="btn-warning" onclick="toggleCategory(${c.id})">
                    Toggle Status
                </button>

                <button class="btn-danger" onclick="deleteCategory(${c.id})">
                    Hapus
                </button>
            </div>
        `;
    });
}

async function createCategory() {
    const name = document.getElementById("categoryName").value;

    await fetch(API_CATEGORIES + "/?name=" + encodeURIComponent(name), {
        method: "POST"
    });

    closeModal();
    loadCategories();
}

async function toggleCategory(id) {
    await fetch(API_CATEGORIES + "/" + id + "/toggle", {
        method: "PATCH"
    });

    loadCategories();
}

async function deleteCategory(id) {
    if (!confirm("Hapus kategori ini?")) return;

    await fetch(API_CATEGORIES + "/" + id, {
        method: "DELETE"
    });

    loadCategories();
}

function openModal() {
    document.getElementById("categoryModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("categoryModal").style.display = "none";
}

loadCategories();