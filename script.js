const filesys = require("fs");

const submit = document.querySelector(".log");
const name1 = document.querySelector(".name");
const email = document.querySelector(".email");
const states = document.querySelector(".drop-states");
const password = document.querySelector(".password1");
const confirmpassword = document.querySelector(".password2");

submit.addEventListener("click",()=>{
    if(name1.value == ""||email.value == ""||password.value == ""||confirmpassword.value == ""){
        if(name1.value == ""){
            document.querySelector(".invalid-name").style="display:block;"
            name1.style="border:2px solid red;"
        }
        if(email.value == ""){
            document.querySelector(".invalid-email").style="display:block;";
            email.style="border:2px solid red;"
        }
        if(password.value == ""){
            document.querySelector(".invalid-password1").style="display:block;";
            password.style="border:2px solid red;"
        }
        if(confirmpassword.value == ""){
            document.querySelector(".invalid-password2").style="display:block;";
            confirmpassword.style="border:2px solid red;"
        }
    }else{
        if(confirmpassword.value!=password.value){
            document.querySelector(".invalid-password2").style="display:block;";
            confirmpassword.style="border:2px solid red;"
        }else{
            filesys.createReadStream


            
        }
    }

})
