import React, { useEffect, useState } from 'react';
import { Profile } from '../../types';
import { api } from '../../services/api';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { DashboardSkeleton } from '../../components/common/LoadingSkeleton';
import {
  User,
  Mail,
  Phone,
  Building,
  GraduationCap,
  Calendar,
  ShieldCheck,
  CheckCircle,
  Hash,
} from 'lucide-react';

interface ProfilePageProps {
  currentUser: Profile;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ currentUser }) => {
  const [profile, setProfile] = useState<Profile>(currentUser);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadLatestProfile() {
      setLoading(true);
      try {
        const data = await api.getStudentProfile(currentUser.id);
        if (data) {
          setProfile(data);
        }
      } catch (err) {
        console.error('Failed to load profile:', err);
      } finally {
        setLoading(false);
      }
    }
    loadLatestProfile();
  }, [currentUser]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Profile Header Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs flex flex-col sm:flex-row items-center sm:items-start gap-6 text-center sm:text-left">
        <div className="w-24 h-24 rounded-2xl bg-[#17365D] text-white flex items-center justify-center font-bold text-3xl shadow-md shrink-0">
          {profile.full_name ? profile.full_name.charAt(0).toUpperCase() : 'U'}
        </div>
        <div className="flex-1 space-y-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">
                {profile.full_name}
              </h2>
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 mt-1">
                <span className="font-mono text-xs px-2.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold">
                  {profile.roll_number || 'STU-001'}
                </span>
                <Badge variant="primary" size="sm">
                  {profile.role.toUpperCase()}
                </Badge>
                <span className="inline-flex items-center gap-1 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200 font-medium">
                  <CheckCircle className="w-3 h-3 text-emerald-600" />
                  Active Enrollment
                </span>
              </div>
            </div>
          </div>
          <p className="text-sm text-slate-600">
            {profile.department || 'Department of Computer Science & Engineering'}
          </p>
        </div>
      </div>

      {/* Academic Identity & Record Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Academic Program Card */}
        <Card className="border border-slate-200 shadow-xs">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
            <GraduationCap className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-bold text-slate-900">
              Academic Information
            </h3>
          </div>

          <div className="space-y-3.5 text-sm">
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-500 flex items-center gap-2">
                <Building className="w-4 h-4 text-slate-400" />
                Department
              </span>
              <span className="font-medium text-slate-900">
                {profile.department || 'Computer Science & Engineering'}
              </span>
            </div>

            <div className="flex justify-between items-center py-1 border-t border-slate-100">
              <span className="text-slate-500 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-slate-400" />
                Current Semester
              </span>
              <span className="font-mono font-medium text-slate-900">
                Semester VI (Section A)
              </span>
            </div>

            <div className="flex justify-between items-center py-1 border-t border-slate-100">
              <span className="text-slate-500 flex items-center gap-2">
                <Hash className="w-4 h-4 text-slate-400" />
                Academic Batch
              </span>
              <span className="font-mono font-medium text-slate-900">
                2022 – 2026
              </span>
            </div>

            <div className="flex justify-between items-center py-1 border-t border-slate-100">
              <span className="text-slate-500 flex items-center gap-2">
                <GraduationCap className="w-4 h-4 text-slate-400" />
                Degree Program
              </span>
              <span className="font-medium text-slate-900">
                Bachelor of Technology (B.Tech)
              </span>
            </div>
          </div>
        </Card>

        {/* Contact & System Identity Card */}
        <Card className="border border-slate-200 shadow-xs">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
            <ShieldCheck className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-bold text-slate-900">
              Contact & Auth Identity
            </h3>
          </div>

          <div className="space-y-3.5 text-sm">
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-500 flex items-center gap-2">
                <Mail className="w-4 h-4 text-slate-400" />
                Official Email
              </span>
              <span className="font-mono font-medium text-slate-900">
                {profile.email}
              </span>
            </div>

            <div className="flex justify-between items-center py-1 border-t border-slate-100">
              <span className="text-slate-500 flex items-center gap-2">
                <Phone className="w-4 h-4 text-slate-400" />
                Contact Phone
              </span>
              <span className="font-mono font-medium text-slate-900">
                {profile.phone || '+91 98765 43210'}
              </span>
            </div>

            <div className="flex justify-between items-center py-1 border-t border-slate-100">
              <span className="text-slate-500 flex items-center gap-2">
                <User className="w-4 h-4 text-slate-400" />
                System User ID
              </span>
              <span className="font-mono text-xs text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                {profile.id}
              </span>
            </div>

            <div className="flex justify-between items-center py-1 border-t border-slate-100">
              <span className="text-slate-500 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-slate-400" />
                Authentication Role
              </span>
              <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {profile.role.toUpperCase()}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Identity Grounding Disclosure */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs text-slate-600 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="text-slate-800">CSIC Student Identity Guarantee:</strong> When you converse with the CSIC Academic Assistant on the <span className="font-semibold text-blue-700">AI Chatbot</span> page, all responses regarding attendance percentages, examination marks, timetable schedules, and fee invoices are strictly filtered by your authenticated user ID (<code className="font-mono text-slate-800 bg-slate-200 px-1 rounded">{profile.id}</code>). You are always seeing your genuine academic records.
        </div>
      </div>
    </div>
  );
};
