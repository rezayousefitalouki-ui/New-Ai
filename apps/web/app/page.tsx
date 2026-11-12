import { Activity, CalendarDays, Instagram, Lightbulb, Sparkles } from "lucide-react";

const nav = ["داشبورد", "حساب‌های اینستاگرام", "تحلیل‌ها", "دستیار هوشمند", "تقویم محتوا"];
const icons = [Activity, Instagram, Activity, Sparkles, CalendarDays];
const metrics = [
  ["دنبال‌کننده‌ها", "—", "پس از اتصال حساب نمایش داده می‌شود", Instagram],
  ["تعامل محتوا", "—", "هنوز داده‌ای ثبت نشده", Activity],
  ["محتوای این ماه", "۰", "محتوایی برنامه‌ریزی نشده", CalendarDays],
  ["ایده‌های آماده", "۰", "ایدهٔ ذخیره‌شده‌ای وجود ندارد", Lightbulb],
];

export default function Home() {
  return <main className="layout">
    <aside className="sidebar">
      <div className="brand"><span className="brandIcon"><Sparkles size={18}/></span><span>SocialMind <b>AI</b></span></div>
      <button className="workspace"><span className="dot"/> فضای کاری من <span className="down">⌄</span></button>
      <small className="label">فضای کار</small>
      <nav>{nav.map((item,i)=>{const Icon=icons[i];return <a className={i===0?"nav active":"nav"} href="#" key={item}><Icon size={17}/>{item}</a>})}</nav>
      <div className="profile"><span className="avatar">ر</span><span><b>مدیر فضای کار</b><small>پلن آزمایشی</small></span><span className="down">···</span></div>
    </aside>
    <section className="main">
      <header><span>فضای کار <i>/</i> <b>داشبورد</b></span><span className="avatar small">ر</span></header>
      <div className="page">
        <div className="welcome"><div><small>داشبورد فضای کاری</small><h1>خوش آمدی</h1><p>عملکرد محتوایت را ببین و برای قدم بعدی آماده شو.</p></div><button className="primary"><Sparkles size={16}/> ساخت ایدهٔ محتوا</button></div>
        <div className="notice"><span className="noticeIcon"><Instagram size={18}/></span><div><b>حساب اینستاگرامی متصل نیست</b><small>برای دریافت آمار، حساب حرفه‌ای خودت را از مسیر رسمی Meta وصل کن.</small></div><button>اتصال حساب ←</button></div>
        <div className="sectionTitle"><div><b>نمای کلی</b><small>آخرین وضعیت فضای کاری</small></div><button className="period">۷ روز گذشته　⌄</button></div>
        <div className="metrics">{metrics.map(([title,value,caption,Icon])=>{const I=Icon as typeof Activity;return <article className="card metric" key={title as string}><div><span>{title as string}</span><I size={17}/></div><strong>{value as string}</strong><small>{caption as string}</small></article>})}</div>
        <div className="bottom">
          <article className="card chart"><div className="sectionTitle"><div><b>روند تعامل</b><small>عملکرد محتوای منتشرشده</small></div><span>···</span></div><div className="empty"><Activity size={25}/><b>هنوز داده‌ای برای نمایش نداریم</b><small>بعد از اتصال حساب و دریافت آمار، روند تعامل نمایش داده می‌شود.</small></div></article>
          <article className="card quick"><div className="sectionTitle"><div><b>شروع سریع</b><small>قدم بعدی برای فضای کاری</small></div></div>{[["اتصال حساب حرفه‌ای","دریافت امن آمار از API رسمی Meta",Instagram],["تعریف هویت برند","لحن و مخاطب کسب‌وکارت را مشخص کن",Lightbulb],["ساخت اولین ایده","پیشنهادهای متناسب با برندت بگیر",Sparkles]].map(([title,desc,Icon])=>{const I=Icon as typeof Sparkles;return <div className="quickRow" key={title as string}><I size={17}/><span><b>{title as string}</b><small>{desc as string}</small></span><i>←</i></div>})}</article>
        </div>
        <footer>SocialMind AI <span>·</span> دستیار هوشمند رشد محتوا</footer>
      </div>
    </section>
  </main>;
}
