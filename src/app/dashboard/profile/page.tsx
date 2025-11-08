"use client";

import { useState, useEffect } from 'react';
import { createClient } from '@/utils/supabase/client';
import { User, Mail, User as UserIcon, Calendar, Edit, Save, Trash2, Shield, Bell, Lock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import Toast from '@/components/toast';

interface UserProfile {
  id: string;
  email?: string;
  user_metadata?: {
    username?: string;
    full_name?: string;
    avatar_url?: string;
  };
  created_at?: string;
  last_sign_in_at?: string;
}

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState<'success' | 'error'>('success');

  // Form state
  const [formData, setFormData] = useState({
    username: '',
    full_name: '',
    email: '',
  });

  useEffect(() => {
    const fetchUser = async () => {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      
      if (user) {
        setUser(user);
        setFormData({
          username: user.user_metadata?.username || '',
          full_name: user.user_metadata?.full_name || '',
          email: user.email || '',
        });
      }
      setLoading(false);
    };

    fetchUser();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    const supabase = createClient();

    try {
      const { error } = await supabase.auth.updateUser({
        data: {
          username: formData.username,
          full_name: formData.full_name,
        }
      });

      if (error) throw error;

      // Update local user state
      setUser(prev => prev ? {
        ...prev,
        user_metadata: {
          ...prev.user_metadata,
          username: formData.username,
          full_name: formData.full_name,
        }
      } : null);

      setEditing(false);
      showToastMessage('Profile updated successfully!', 'success');
    } catch (error) {
      console.error('Error updating profile:', error);
      showToastMessage('Failed to update profile. Please try again.', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    const supabase = createClient();
    
    try {
      // Note: This is a destructive action. You might want to implement soft delete
      // or ask users to contact support instead of immediate deletion
      const { error } = await supabase.auth.admin.deleteUser(user!.id);
      
      if (error) throw error;
      
      // Sign out after account deletion
      await supabase.auth.signOut();
      showToastMessage('Account deleted successfully', 'success');
      
      // Redirect will happen through the signOut function
    } catch (error) {
      console.error('Error deleting account:', error);
      showToastMessage('Failed to delete account. Please contact support.', 'error');
    }
  };

  const showToastMessage = (message: string, type: 'success' | 'error') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">Please sign in to view your profile.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <Toast
        message={toastMessage}
        type={toastType}
        isVisible={showToast}
        onClose={() => setShowToast(false)}
        duration={3000}
      />

      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
            <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
          </div>
          {!editing ? (
            <Button onClick={() => setEditing(true)} className="flex items-center gap-2">
              <Edit className="h-4 w-4" />
              Edit Profile
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setEditing(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={saving} className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Profile Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information Card */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UserIcon className="h-5 w-5" />
                  Personal Information
                </CardTitle>
                <CardDescription>
                  Update your personal details and how others see you on the platform.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    {editing ? (
                      <Input
                        id="username"
                        value={formData.username}
                        onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                        placeholder="Enter your username"
                      />
                    ) : (
                      <p className="text-sm text-gray-900 p-2 bg-gray-50 rounded">
                        {user.user_metadata?.username || 'Not set'}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="full_name">Full Name</Label>
                    {editing ? (
                      <Input
                        id="full_name"
                        value={formData.full_name}
                        onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
                        placeholder="Enter your full name"
                      />
                    ) : (
                      <p className="text-sm text-gray-900 p-2 bg-gray-50 rounded">
                        {user.user_metadata?.full_name || 'Not set'}
                      </p>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    Email Address
                  </Label>
                  <p className="text-sm text-gray-600 p-2 bg-gray-50 rounded">
                    {user.email}
                    <span className="ml-2 text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
                      Verified
                    </span>
                  </p>
                  <p className="text-xs text-gray-500">
                    Email cannot be changed. Contact support for email modifications.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Account Statistics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Account Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Member Since</Label>
                    <p className="text-sm text-gray-600">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <Label>Last Login</Label>
                    <p className="text-sm text-gray-600">
                      {user.last_sign_in_at ? new Date(user.last_sign_in_at).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <Label>User ID</Label>
                    <p className="text-sm text-gray-600 font-mono truncate">
                      {user.id}
                    </p>
                  </div>
                  <div>
                    <Label>Account Status</Label>
                    <p className="text-sm text-green-600 bg-green-100 px-2 py-1 rounded-full inline-block">
                      Active
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Preferences */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Preferences
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="email-notifications">Email Notifications</Label>
                    <p className="text-xs text-gray-500">Receive job alerts and updates</p>
                  </div>
                  <Switch id="email-notifications" defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="newsletter">Newsletter</Label>
                    <p className="text-xs text-gray-500">Weekly job search tips</p>
                  </div>
                  <Switch id="newsletter" />
                </div>
              </CardContent>
            </Card>

            {/* Security */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Security
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start" asChild>
                  <a href="/dashboard/change-password">
                    <Lock className="h-4 w-4 mr-2" />
                    Change Password
                  </a>
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Shield className="h-4 w-4 mr-2" />
                  Two-Factor Authentication
                </Button>
              </CardContent>
            </Card>

            {/* Danger Zone */}
            <Card className="border-red-200">
              <CardHeader>
                <CardTitle className="text-red-600 flex items-center gap-2">
                  <Trash2 className="h-5 w-5" />
                  Danger Zone
                </CardTitle>
                <CardDescription>
                  Permanent actions that cannot be undone
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive" className="w-full">
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Account
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This action cannot be undone. This will permanently delete your account
                        and remove all your data from our servers. All your job applications,
                        cover letters, and profile information will be lost.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction 
                        onClick={handleDeleteAccount}
                        className="bg-red-600 hover:bg-red-700"
                      >
                        Delete Account
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}