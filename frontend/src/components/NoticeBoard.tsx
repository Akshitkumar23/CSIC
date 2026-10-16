import React, { useState } from 'react';
import { Notice, NoticeCategory } from '../types';
import { Card } from './common/Card';
import { Badge } from './common/Badge';
import { Modal } from './common/Modal';
import { Megaphone, Calendar, User, ChevronRight } from 'lucide-react';

interface NoticeBoardProps {
  notices: Notice[];
}

const CATEGORIES: { label: string; value: string }[] = [
  { label: 'All Circulars', value: 'all' },
  { label: 'Urgent', value: 'urgent' },
  { label: 'Academic', value: 'academic' },
  { label: 'Examinations', value: 'examination' },
  { label: 'Fees & Finance', value: 'fees' },
  { label: 'Administrative', value: 'administrative' },
  { label: 'Campus Events', value: 'event' },
];

export const NoticeBoard: React.FC<NoticeBoardProps> = ({ notices }) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [activeNotice, setActiveNotice] = useState<Notice | null>(null);

  const filteredNotices = notices.filter(
    (n) => selectedCategory === 'all' || n.category === selectedCategory
  );

  const getCategoryBadge = (cat: NoticeCategory) => {
    switch (cat) {
      case 'urgent':
        return <Badge variant="danger" size="sm">URGENT</Badge>;
      case 'examination':
        return <Badge variant="warning" size="sm">EXAMINATION</Badge>;
      case 'academic':
        return <Badge variant="primary" size="sm">ACADEMIC</Badge>;
      case 'fees':
        return <Badge variant="warning" size="sm">FEES</Badge>;
      case 'administrative':
        return <Badge variant="neutral" size="sm">ADMIN</Badge>;
      case 'event':
        return <Badge variant="info" size="sm">EVENT</Badge>;
    }
  };

  return (
    <>
      <Card id="notices-section" className="overflow-hidden">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Megaphone className="w-5 h-5 text-indigo-400" />
              Institutional Notice Board
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Official circulars, regulatory announcements, and events
            </p>
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-6 border-b border-white/5 scrollbar-thin">
          {CATEGORIES.map((cat) => {
            const count =
              cat.value === 'all'
                ? notices.length
                : notices.filter((n) => n.category === cat.value).length;
            const isActive = selectedCategory === cat.value;

            return (
              <button
                key={cat.value}
                onClick={() => setSelectedCategory(cat.value)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all whitespace-nowrap flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'bg-slate-800/40 text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <span>{cat.label}</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-900/40">
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Notices Stream */}
        <div className="space-y-3">
          {filteredNotices.length === 0 ? (
            <div className="p-8 text-center text-slate-400 bg-slate-900/30 rounded-xl border border-white/5">
              No notices published under this category.
            </div>
          ) : (
            filteredNotices.map((notice) => (
              <div
                key={notice.id}
                onClick={() => setActiveNotice(notice)}
                className={`p-4 rounded-xl border transition-all cursor-pointer group ${
                  notice.is_urgent || notice.category === 'urgent'
                    ? 'bg-rose-950/20 border-rose-500/30 hover:border-rose-500/60'
                    : 'bg-slate-800/40 border-white/5 hover:border-indigo-500/30 hover:bg-slate-800/80'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2">
                      {getCategoryBadge(notice.category)}
                      <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {notice.published_at.substring(0, 10)}
                      </span>
                    </div>

                    <h4 className="text-sm font-semibold text-white group-hover:text-indigo-200 transition-colors">
                      {notice.title}
                    </h4>

                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                      {notice.content}
                    </p>

                    <div className="flex items-center gap-1.5 text-[11px] text-slate-500 pt-1">
                      <User className="w-3 h-3" />
                      <span>{notice.published_by_name}</span>
                    </div>
                  </div>

                  <div className="self-center p-1 rounded-lg text-slate-500 group-hover:text-indigo-300 group-hover:translate-x-1 transition-all">
                    <ChevronRight className="w-5 h-5" />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Notice Detail Modal */}
      {activeNotice && (
        <Modal
          isOpen={!!activeNotice}
          onClose={() => setActiveNotice(null)}
          title={activeNotice.title}
          maxWidth="lg"
        >
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-white/10 text-xs">
              <div className="flex items-center gap-2">
                {getCategoryBadge(activeNotice.category)}
                <span className="text-slate-400">Target: {activeNotice.target_role.toUpperCase()}</span>
              </div>
              <span className="text-slate-400 font-mono">
                {activeNotice.published_at}
              </span>
            </div>

            <div className="text-sm text-slate-200 whitespace-pre-line leading-relaxed bg-slate-900/60 p-4 rounded-xl border border-white/5">
              {activeNotice.content}
            </div>

            <div className="text-xs text-slate-400 flex items-center justify-between pt-2">
              <span>Published by: <strong>{activeNotice.published_by_name}</strong></span>
              <span className="font-mono text-slate-500">CSIC Verified Circular</span>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
};
