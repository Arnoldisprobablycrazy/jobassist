"use server";

import { revalidatePath } from "next/cache"
import { redirect } from "next/navigation";
import { createClient } from "@utils/supabase/server";

export async function signUp(formData: FormData) {
    const supabase = await createClient()

    const credentials = {
        username: formData.get("username") as string,
        email: formData.get("email") as string,
        password: formData.get("password") as string,
    }
    
    // Basic validation
    if (!credentials.email || !credentials.password || !credentials.username) {
        return {
            status: "All fields are required",
            user: null,
        };
    }

    if (credentials.password.length < 6) {
        return {
            status: "Password must be at least 6 characters",
            user: null,
        };
    }
    
    const { error, data } = await supabase.auth.signUp({
        email: credentials.email,
        password: credentials.password,
        options: {
            data: {
                username: credentials.username,
            },
            emailRedirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
        },
    }); 

    if (error) {
        console.error('SignUp error:', error.message);
        
        // Handle specific error cases
        if (error.message.includes('already registered')) {
            return {
                status: "Email already exists, please login instead",
                user: null,
            };
        }
        
        return {
            status: error.message,
            user: null,
        };
    }

    // Check if user already exists (identities array empty)
    if (data?.user && data.user.identities?.length === 0) {
        return {
            status: "Email already exists, please login instead",
            user: null,
        };
    }
    
    revalidatePath("/", "layout");
    return { 
        status: "success", 
        user: data.user,
        message: "Account created! Please check your email for verification."
    };
}

export async function signIn(formData: FormData) {
    const supabase = await createClient()

    const credentials = {
        email: formData.get("email") as string,
        password: formData.get("password") as string,
    }
    
    // Basic validation
    if (!credentials.email || !credentials.password) {
        return {
            status: "Email and password are required",
            user: null,
        };
    }
    
    const { error, data } = await supabase.auth.signInWithPassword(credentials)

    if (error) {
        console.error('SignIn error:', error.message);
        
        // Handle specific error cases
        if (error.message.includes('Email not confirmed')) {
            return {
                status: "Email not confirmed",
                user: null,
            };
        }
        
        if (error.message.includes('Invalid login credentials')) {
            return {
                status: "Invalid email or password",
                user: null,
            };
        }
        
        return {
            status: error.message,
            user: null,
        };
    }
    
    revalidatePath("/", "layout");
    return { 
        status: "success", 
        user: data.user 
    };
}

export async function signOut() {
    const supabase = await createClient()

    const { error } = await supabase.auth.signOut();

    if (error) {
        console.error('SignOut error:', error.message);
        redirect("/error");
    }
    
    revalidatePath("/", "layout");
    redirect("/");
}

export async function promoteToAdmin(userId: string) {
    const supabase = await createClient();
    
    // Check if current user is authenticated
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
        return { error: "Not authenticated" };
    }
    
    // Check if current user is admin
    const { data: currentUserData, error: fetchError } = await supabase
        .from("profiles")
        .select("role")
        .eq("id", user.id)
        .single();
    
    if (fetchError) {
        console.error('Fetch user role error:', fetchError.message);
        return { error: "Failed to verify permissions" };
    }
    
    if (currentUserData?.role !== "admin") {
        return { error: "Unauthorized: Admin access required" };
    }
    
    // Update the user's role
    const { error } = await supabase
        .from("profiles")
        .update({ role: "admin" })
        .eq("id", userId);
    
    if (error) {
        console.error('Promote to admin error:', error.message);
        return { error: error.message };
    }
    
    revalidatePath("/role");
    return { success: true };
}

export async function resendVerificationEmail(email: string) {
    const supabase = await createClient();
    
    // Validate email
    if (!email) {
        return { status: "Email is required" };
    }
    
    const { error } = await supabase.auth.resend({
        type: 'signup',
        email: email,
        options: {
            emailRedirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
        },
    });

    if (error) {
        console.error('Resend verification error:', error.message);
        return { status: error.message };
    }

    return { 
        status: "success",
        message: "Verification email sent successfully!"
    };
}

// Additional utility function to check auth status
export async function getCurrentUser() {
    const supabase = await createClient();
    
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error) {
        console.error('Get current user error:', error.message);
        return { user: null, error: error.message };
    }
    
    return { user, error: null };
}

// Function to update user profile
export async function updateUserProfile(userId: string, updates: { username?: string }) {
    const supabase = await createClient();
    
    const { error } = await supabase
        .from("profiles")
        .update(updates)
        .eq("id", userId);
    
    if (error) {
        console.error('Update profile error:', error.message);
        return { error: error.message };
    }
    
    revalidatePath("/profile");
    return { success: true };
}