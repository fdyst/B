const API_PRODUCTS = "/products";
const API_CATEGORIES = "/categories";

/* =========================
   CATEGORY FUNCTIONS
========================= */

async function loadCategories() {
    const res = await fetch(API_CATEGORIES + "/");
    const data = await res.json();

    const filter = document.getElementById("categoryFilter");
    const select = document.getElementById("categorySelect");

    filter.innerHTML = `<option value="">Semua Kategori</option>`;
    select.innerHTML = "";

    data.forEach(c=>{
        filter.innerHTML += `<option value="${c.id}">${c.name}</option>`;
        select.innerHTML += `<option value="${c.id}">${c.name}</option>`;
    });
}

async function loadCategoryAdminList(){
    const res = await fetch(API_CATEGORIES + "/");
    const data = await res.json();

    const container = document.getElementById("categoryListAdmin");
    container.innerHTML = "";

    data.forEach(c=>{
        container.innerHTML += `
        <div class="card">
            <strong>${c.name}</strong>
            <div>Status: ${c.is_active?"🟢":"🔴"}</div>

            <button class="btn-warning"
            onclick="editCategory(${c.id},'${c.name}')">Edit</button>

            <button class="btn-success"
            onclick="toggleCategory(${c.id})">Toggle</button>

            <button class="btn-danger"
            onclick="deleteCategory(${c.id})">Hapus</button>
        </div>`;
    });
}

async function createCategory(){
    const name=document.getElementById("newCategoryName").value;

    await fetch(API_CATEGORIES + "/?name=" + encodeURIComponent(name),{
        method:"POST"
    });

    document.getElementById("newCategoryName").value="";
    loadCategoryAdminList();
    loadCategories();
}

async function editCategory(id,oldName){
    const newName=prompt("Edit kategori:",oldName);
    if(!newName)return;

    await fetch(API_CATEGORIES + "/" + id + "?name=" + encodeURIComponent(newName),{
        method:"PUT"
    });

    loadCategoryAdminList();
    loadCategories();
}

async function deleteCategory(id){
    if(!confirm("Hapus kategori ini?"))return;

    await fetch(API_CATEGORIES + "/" + id,{
        method:"DELETE"
    });

    loadCategoryAdminList();
    loadCategories();
}

async function toggleCategory(id){
    await fetch(API_CATEGORIES + "/" + id + "/toggle",{
        method:"PATCH"
    });

    loadCategoryAdminList();
    loadCategories();
}

function openCategoryModal(){
    document.getElementById("categoryModal").style.display="flex";
    loadCategoryAdminList();
}
function closeCategoryModal(){
    document.getElementById("categoryModal").style.display="none";
}

/* =========================
   PRODUCT FUNCTIONS
========================= */

async function loadProducts(){
    const res=await fetch(API_PRODUCTS);
    const data=await res.json();

    const filter=document.getElementById("categoryFilter").value;
    const container=document.getElementById("productList");
    container.innerHTML="";

    let filtered=data;
    if(filter){
        filtered=data.filter(p=>p.category_id==filter);
    }

    if(!filtered.length){
        container.innerHTML="<p>Tidak ada produk</p>";
        return;
    }

    filtered.forEach(p=>{
        container.innerHTML+=`
        <div class="card">
            <strong>${p.name}</strong>
            <div>Harga: Rp ${p.price_sell}</div>
            <div>Stok: ${p.stock_count ?? 0}</div>
            <div>Status: ${p.is_active?"🟢":"🔴"}</div>

            <button class="btn-warning"
            onclick="toggleProduct(${p.id})">Toggle</button>

            <input type="file"
            onchange="uploadStock(${p.id},this)">

            <button class="btn-danger"
            onclick="deleteProduct(${p.id})">Hapus</button>
        </div>`;
    });
}

async function createProduct(){
    const payload={
        name:document.getElementById("name").value,
        category_id:parseInt(document.getElementById("categorySelect").value),
        product_type:document.getElementById("product_type").value,
        price_base:parseFloat(document.getElementById("price_base").value),
        margin_type:document.getElementById("margin_type").value,
        margin_value:parseFloat(document.getElementById("margin_value").value)
    };

    await fetch(API_PRODUCTS+"/",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
    });

    closeCreateModal();
    loadProducts();
}

async function deleteProduct(id){
    if(!confirm("Hapus produk?"))return;

    await fetch(API_PRODUCTS+"/"+id,{
        method:"DELETE"
    });

    loadProducts();
}

async function toggleProduct(id){
    await fetch(API_PRODUCTS+"/"+id+"/toggle",{
        method:"PATCH"
    });

    loadProducts();
}

async function uploadStock(id,input){
    const file=input.files[0];
    const formData=new FormData();
    formData.append("file",file);

    await fetch(API_PRODUCTS+"/"+id+"/upload-stock",{
        method:"POST",
        body:formData
    });

    alert("Stock uploaded!");
    loadProducts();
}

function openCreateModal(){
    document.getElementById("createModal").style.display="flex";
}
function closeCreateModal(){
    document.getElementById("createModal").style.display="none";
}

/* INIT */
loadCategories();
loadProducts();