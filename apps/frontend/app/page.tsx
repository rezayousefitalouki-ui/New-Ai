import Link from "next/link";
import { ArrowDownLeft, ArrowUpLeft, CalendarDays, Instagram, Plus, Sparkles, TrendingUp, Video } from "lucide-react";

const metrics = [
  { label: "دنبال‌کننده‌ها", value: "—", change: "اتصال حساب لازم است", icon: Instagram, tone: "mint" },
  { label: "تعامل محتوا", value: "—", change: "داده‌ای دریافت نشده", icon: TrendingUp, tone: "blue" },
  { label: "محتوای برنامه‌ریزی‌شده", value: "۰", change: "در این ماه", icon: CalendarDays, tone: "amber" },
  { label: "اعتبار قابل استفاده", value: "۳۴۰", change: "از ۵۰۰ اعتبار", icon: Sparkles, tone: "violet" },
];

export default function DashboardPage() {
  return <div className="page-content">
    <div className="page-heading"><div><div className="eyebrow">پنج‌شنبه، ۲۱ آبان ۱۴۰۵ <span className="live-dot"/> پیش‌نمایش محصول</div><h1>نمای کلی</h1><p>وضعیت محتوای فضای کاری را از یک‌جا دنبال کن.</p></div><Link href="/studio" className="button-primary"><Plus size={17}/> ساخت محتوای جدید</Link></div>
    <div className="connect-banner"><div className="connect-mark"><Instagram size={19}/></div><div><b>حساب اینستاگرامی هنوز متصل نشده</b><small>برای مشاهدهٔ تحلیل واقعی و برنامه‌ریزی انتشار، حساب حرفه‌ای را متصل کن.</small></div><button className="button-outline">اتصال حساب <ArrowDownLeft size={15}/></button></div>
    <div className="metric-grid">{metrics.map(({label,value,change,icon:Icon,tone})=><article className="surface metric-card" key={label}><div className="metric-head"><span>{label}</span><span className={"metric-icon "+tone}><Icon size={17}/></span></div><strong>{value}</strong><small>{change}</small></article>)}</div>
    <div className="dashboard-grid">
      <section className="surface performance-panel"><div className="panel-head"><div><h2>روند عملکرد</h2><small>آمار در دسترس پس از اتصال حساب نمایش داده می‌شود</small></div><button className="select-control">۳۰ روز اخیر <CalendarDays size={14}/></button></div>
        <div className="chart-legend"><span><i className="legend-dot green"/> تعامل</span><span><i className="legend-dot blue"/> دسترسی</span><span className="muted">دادهٔ واقعی هنوز موجود نیست</span></div>
        <div className="chart-area"><div className="chart-y"><span>۱۰۰</span><span>۷۵</span><span>۵۰</span><span>۲۵</span><span>۰</span></div><div className="chart-grid"><div className="chart-lines"><i/><i/><i/><i/><i/></div><div className="chart-empty-state"><b>داده‌ای برای رسم نمودار نداریم</b><small>پس از اتصال حساب، آمار واقعی اینجا نمایش داده می‌شود.</small></div><div className="chart-x"><span>۱ آبان</span><span>۸ آبان</span><span>۱۵ آبان</span><span>۲۲ آبان</span><span>۳۰ آبان</span></div></div></div>
      </section>
      <section className="surface quick-panel"><div className="panel-head"><div><h2>شروع سریع</h2><small>قدم‌های بعدی برای فضای کاری</small></div><button className="quiet-icon">···</button></div>
        <Link href="#" className="quick-row"><span className="quick-icon mint"><Instagram size={17}/></span><span><b>اتصال حساب حرفه‌ای</b><small>دریافت امن داده از API رسمی Meta</small></span><ArrowUpLeft size={15}/></Link>
        <Link href="#" className="quick-row"><span className="quick-icon violet"><Sparkles size={17}/></span><span><b>تعریف هویت برند</b><small>لحن، مخاطب و محصولاتت را ثبت کن</small></span><ArrowUpLeft size={15}/></Link>
        <Link href="/calendar" className="quick-row"><span className="quick-icon amber"><CalendarDays size={17}/></span><span><b>چیدن تقویم محتوا</b><small>برای انتشار منظم برنامه‌ریزی کن</small></span><ArrowUpLeft size={15}/></Link>
        <Link href="/studio" className="quick-row"><span className="quick-icon blue"><Video size={17}/></span><span><b>ساخت اولین ویدیو</b><small>وارد استودیوی تولید محتوا شو</small></span><ArrowUpLeft size={15}/></Link>
      </section>
    </div>
    <div className="bottom-grid">
      <section className="surface recent-panel"><div className="panel-head"><div><h2>محتوای اخیر</h2><small>پیش‌نویس‌ها و محتوای در صف بررسی</small></div><Link href="/calendar" className="subtle-link">نمایش تقویم ←</Link></div><div className="empty-state"><span><Video size={21}/></span><b>هنوز محتوایی ساخته نشده</b><small>اولین ایده یا ویدیویت را بساز تا اینجا ببینی.</small><Link href="/studio">رفتن به استودیو <ArrowUpLeft size={14}/></Link></div></section>
      <section className="surface schedule-panel"><div className="panel-head"><div><h2>برنامهٔ امروز</h2><small>پنج‌شنبه، ۲۱ آبان</small></div><CalendarDays size={17}/></div><div className="empty-state compact"><span><CalendarDays size={19}/></span><b>انتشاری برای امروز نیست</b><small>محتوای زمان‌بندی‌شده در این بخش می‌آید.</small><Link href="/calendar">باز کردن تقویم <ArrowUpLeft size={14}/></Link></div></section>
    </div>
    <div className="data-note">داده‌های این داشبورد واقعی و زنده نیستند تا وقتی حساب شبکهٔ اجتماعی متصل شود.</div>
  </div>;
}
