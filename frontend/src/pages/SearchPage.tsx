import React, { useEffect, useState } from 'react';
import {
  Search,
  Filter,
  BookOpen,
  Calendar,
  Award,
  CreditCard,
  HelpCircle,
  FileText,
  X,
  ExternalLink,
  RefreshCw,
  SlidersHorizontal,
} from 'lucide-react';
import { SearchItem } from '../types';
import { api } from '../services/api';
import { Badge } from '../components/common/Badge';
import { EmptyState } from '../components/common/EmptyState';
import { DashboardSkeleton } from '../components/common/LoadingSkeleton';

const CATEGORIES = [
  { id: 'all', label: 'All Categories', icon: SlidersHorizontal },
  { id: 'Syllabus', label: 'Syllabus', icon: BookOpen, variant: 'primary' as const },
  { id: 'Timetable', label: 'Timetable', icon: Calendar, variant: 'info' as const },
  { id: 'Results', label: 'Results', icon: Award, variant: 'success' as const },
  { id: 'Fees', label: 'Fees', icon: CreditCard, variant: 'warning' as const },
  { id: 'FAQ', label: 'FAQ', icon: HelpCircle, variant: 'neutral' as const },
];

const BRANCH_OPTIONS = [
  { value: '', label: 'All Branches' },
  { value: 'Computer Science & Engineering', label: 'Computer Science & Engineering (CSE)' },
];

const YEAR_OPTIONS = [
  { value: '', label: 'All Years' },
  { value: '1', label: '1st Year' },
  { value: '2', label: '2nd Year' },
  { value: '3', label: '3rd Year' },
  { value: '4', label: '4th Year' },
];

export const SearchPage: React.FC = () => {
  const [items, setItems] = useState<SearchItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedBranch, setSelectedBranch] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');

  const hasActiveFilters = Boolean(
    searchQuery || (selectedCategory && selectedCategory !== 'all') || selectedBranch || selectedYear || selectedSubject
  );

  const [reloadTrigger, setReloadTrigger] = useState(0);

  const fetchResults = () => {
    setReloadTrigger((prev) => prev + 1);
  };

  // Single unified debounced effect with cancellation to avoid duplicate requests & race conditions
  useEffect(() => {
    let cancelled = false;
    const isTyping = Boolean(searchQuery.trim() || selectedSubject.trim());
    const delay = isTyping ? 300 : 0;

    const handler = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const params: {
          branch?: string;
          year?: number;
          category?: string;
          subject?: string;
          q?: string;
        } = {};

        if (searchQuery.trim()) params.q = searchQuery.trim();
        if (selectedCategory && selectedCategory !== 'all') params.category = selectedCategory;
        if (selectedBranch) params.branch = selectedBranch;
        if (selectedYear) params.year = parseInt(selectedYear, 10);
        if (selectedSubject.trim()) params.subject = selectedSubject.trim();

        const data = await api.searchInformation(params);
        if (!cancelled) {
          setItems(data);
        }
      } catch (err: any) {
        if (!cancelled) {
          console.error('Failed to load search results:', err);
          setError(err.message || 'Unable to load search information.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }, delay);

    return () => {
      cancelled = true;
      clearTimeout(handler);
    };
  }, [searchQuery, selectedCategory, selectedBranch, selectedYear, selectedSubject, reloadTrigger]);


  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedCategory('all');
    setSelectedBranch('');
    setSelectedYear('');
    setSelectedSubject('');
  };

  const getCategoryBadgeVariant = (cat: string) => {
    switch (cat.toLowerCase()) {
      case 'syllabus':
        return 'primary';
      case 'timetable':
        return 'info';
      case 'results':
        return 'success';
      case 'fees':
        return 'warning';
      case 'faq':
      default:
        return 'neutral';
    }
  };

  const getCategoryIcon = (cat: string) => {
    switch (cat.toLowerCase()) {
      case 'syllabus':
        return <BookOpen className="w-3.5 h-3.5" />;
      case 'timetable':
        return <Calendar className="w-3.5 h-3.5" />;
      case 'results':
        return <Award className="w-3.5 h-3.5" />;
      case 'fees':
        return <CreditCard className="w-3.5 h-3.5" />;
      case 'faq':
      default:
        return <HelpCircle className="w-3.5 h-3.5" />;
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-xs relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-2 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
                <Search className="w-5 h-5" />
              </span>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                Search Information
              </h1>
            </div>
            <p className="text-sm text-slate-500 max-w-xl">
              Quickly find academic syllabus, lecture timetables, examination marks, fee structures, and institutional regulations.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto">
            <span className="text-xs font-semibold px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
              {items.length} {items.length === 1 ? 'Record found' : 'Records found'}
            </span>
          </div>
        </div>
      </div>

      {/* Filter and Search Panel */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs space-y-4">
        {/* Search Query Bar */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by keywords, topic, syllabus units, or rules (e.g. Virtualization, AWS, Lab-204)..."
            className="w-full pl-10 pr-10 py-2.5 text-sm bg-slate-50/70 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all placeholder:text-slate-400"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
              aria-label="Clear search"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Category Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-100">
          <span className="text-xs font-medium text-slate-400 flex items-center gap-1 mr-1">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isSelected = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-slate-100/80 text-slate-600 hover:bg-slate-200/80'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {cat.label}
              </button>
            );
          })}
        </div>

        {/* Secondary Filter Dropdowns */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-slate-100">
          {/* Branch Selector */}
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Branch</label>
            <select
              value={selectedBranch}
              onChange={(e) => setSelectedBranch(e.target.value)}
              className="w-full text-xs py-2 px-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 text-slate-700"
            >
              {BRANCH_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Year Selector */}
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Academic Year</label>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="w-full text-xs py-2 px-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 text-slate-700"
            >
              {YEAR_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Subject Filter Input */}
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Subject / Domain</label>
            <input
              type="text"
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              placeholder="e.g. Cloud Computing, Database..."
              className="w-full text-xs py-2 px-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 text-slate-700 placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Active Filters Clear Button */}
        {hasActiveFilters && (
          <div className="flex items-center justify-between pt-2 text-xs border-t border-slate-100 text-slate-500">
            <span>Filtering applied</span>
            <button
              onClick={handleResetFilters}
              className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" /> Reset all filters
            </button>
          </div>
        )}
      </div>

      {/* Results View */}
      {loading ? (
        <DashboardSkeleton />
      ) : error ? (
        <div className="p-8 bg-white rounded-2xl border border-rose-200 text-center space-y-3">
          <p className="text-sm text-rose-600 font-medium">{error}</p>
          <button
            onClick={fetchResults}
            className="px-4 py-2 bg-blue-600 text-white text-xs font-semibold rounded-xl hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          title="No Matching Information Found"
          description={
            hasActiveFilters
              ? 'Try relaxing your filter criteria or searching with broader keywords.'
              : 'No records available in the search database.'
          }
          icon={<Search className="w-8 h-8 text-slate-400" />}
          actionLabel={hasActiveFilters ? 'Reset Filters' : undefined}
          onAction={hasActiveFilters ? handleResetFilters : undefined}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs hover:border-slate-300 hover:shadow-sm transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                {/* Meta Badges */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={getCategoryBadgeVariant(item.category)}
                      size="sm"
                      icon={getCategoryIcon(item.category)}
                    >
                      {item.category}
                    </Badge>
                    <span className="text-xs px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 font-medium border border-slate-200/60">
                      Year {item.year}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">
                    {item.branch === 'Computer Science & Engineering' ? 'CSE' : item.branch}
                  </span>
                </div>

                {/* Card Title & Subject */}
                <div>
                  <h3 className="text-base font-semibold text-slate-900 leading-snug">
                    {item.title}
                  </h3>
                  <p className="text-xs font-medium text-blue-600 mt-1 flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5" />
                    {item.subject}
                  </p>
                </div>

                {/* Content Details */}
                <p className="text-xs text-slate-600 leading-relaxed bg-slate-50/70 p-3 rounded-xl border border-slate-100">
                  {item.content_details}
                </p>
              </div>

              {/* Card Footer: Document link if available */}
              {item.file_url && (
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400 truncate max-w-[200px]">
                    {item.file_url}
                  </span>
                  <a
                    href={item.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <span>View Document</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
