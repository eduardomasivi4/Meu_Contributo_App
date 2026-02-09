let user = JSON.parse(localStorage.getItem("user")) || {creditos:0,atividades:[]}

function show(id){
document.querySelectorAll('.container > div').forEach(d=>d.classList.add('hidden'))
document.getElementById(id).classList.remove('hidden')
}

function login(){
user.nome = nome.value
user.email = email.value
localStorage.setItem("user",JSON.stringify(user))
atualizar()
show('dashboard')
}

function atualizar(){
userName.innerText = user.nome
credits.innerText = user.creditos
totalCredito.innerText = user.creditos
perfilNome.innerText = user.nome
foto.src = user.foto || ''
lista.innerHTML = user.atividades.map(a=>`<li>${a.nome} — ${a.creditos} créditos</li>`).join('')
}

function registrar(){
let c = parseInt(actCred.value)
if(!c) return alert("Informe os créditos")
user.creditos += c
user.atividades.push({nome:actNome.value,creditos:c})
localStorage.setItem("user",JSON.stringify(user))
atualizar()
show('dashboard')
}

function salvarPerfil(){
user.nome = novoNome.value
user.email = novoEmail.value
localStorage.setItem("user",JSON.stringify(user))
atualizar()
show('perfil')
}

function carregar(e){
let r = new FileReader()
r.onload = ()=>{
user.foto = r.result
localStorage.setItem("user",JSON.stringify(user))
atualizar()
}
r.readAsDataURL(e.target.files[0])
}

function logout(){
localStorage.clear()
location.reload()
}

if(user.nome){
atualizar()
show('dashboard')
}
