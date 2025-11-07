"use server";


import{revalidatePath} from "next/cache"
import { redirect } from "next/navigation";

import { createClient } from "@utils/supabase/server";
import { headers } from "next/headers";

export async function signUp(formData: FormData) {
    const supabase = await createClient()

    const credentials = {
          username: formData.get("username") as string,
          email: formData.get("email") as string,
          password: formData.get("password") as string,
    }
   const {error, data} = await supabase.auth.signUp({
       email: credentials.email,
       password:credentials.password,
       options:{
        data: {
            username: credentials.username,
           
        },
       },
   }); 

   if (error) {
    return {
        status:error.message,
        user:null,
    };
   
   }  else if (data?.user?.identities?.length ===0){
        return{
            status:"Email already exists, please Login",
            user: null,
        }
    }
    revalidatePath("/" , "layout")
    return {status: "success", user:data.user};
}

export async function signIn(formData: FormData){
    const supabase = await createClient()

    const credentials = {
          
          email: formData.get("email") as string,
          password: formData.get("password") as string,
    }
    const {error ,data} = await supabase.auth.signInWithPassword(credentials)

    if(error){
        return{
            status:error.message,
            user:null,
        }
    }
    revalidatePath("/", "layout")
    return {status: "success", user: data.user}
}
export async function signOut(){
    const supabase = await createClient()

    const {error} = await supabase.auth.signOut();

    if(error){
        redirect ("/error")
    }
    revalidatePath("/","layout")
    redirect("/login")
}

export async function promoteToAdmin(userId: string) {
  const supabase = await createClient();
  
  // Check if current user is admin
  const { data: { user } } = await supabase.auth.getUser();
  
  if (!user) {
    return { error: "Not authenticated" };
  }
  
  const { data: currentUserData } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", user.id)
    .single();
  
  if (currentUserData?.role !== "admin") {
    return { error: "Unauthorized: Admin access required" };
  }
  
  // Update the user's role
  const { error } = await supabase
    .from("profiles")
    .update({ role: "admin" })
    .eq("id", userId);
  
  if (error) {
    return { error: error.message };
  }
  
  revalidatePath("/role");
  return { success: true };
}