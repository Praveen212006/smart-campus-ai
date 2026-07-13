function togglePassword(){

let password=document.getElementById("password");

let eye=document.getElementById("eyeIcon");

if(password.type==="password"){

password.type="text";

eye.className="fa fa-eye-slash";

}else{

password.type="password";

eye.className="fa fa-eye";

}

}