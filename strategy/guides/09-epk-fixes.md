# EPK Website Fixes -- Implementation Guide

**Repo**: github.com/allpointsnorthband-art/.github.io
**Live URL**: allpointsnorthband-art.github.io/.github.io
**Local clone**: `/Users/jarno/BMAD/apn-epk/`

---

## Changes Already Made (in local clone)

The following changes have been applied to `index.html` in the local clone at `/Users/jarno/BMAD/apn-epk/`. Push to GitHub to go live.

### 1. Stats Section Updated

The animated counters now show more realistic values:
- Spotify listeners: 150+
- Social followers: 200+
- Shows played: 15+
- Total streams: 3,000+

**Location**: JavaScript at bottom of `index.html`, `animateCounter()` calls.

**Action needed**: Update these numbers quarterly as the band grows. The numbers are in the JS block near the bottom of `index.html`.

### 2. Newsletter Signup Section Added

A new section "Join the Mailing List" has been added between the Photos and Technical sections:
- Nav link added: "Newsletter"
- Email input form with subscribe button
- Placeholder JavaScript that shows a thank-you message
- CSS for the newsletter form included

**Action needed**: Replace the placeholder form with your actual Mailchimp embed code:
1. Go to Mailchimp > Audience > Signup Forms > Embedded Forms
2. Copy the generated HTML
3. Replace the `<form>` block inside `<div id="mc-embedded-form">` with the Mailchimp code
4. Keep the surrounding CSS classes for consistent styling

### 3. Nav Link for Newsletter

Added "Newsletter" link to the navigation bar pointing to `#newsletter`.

---

## Still To Do (Manual Actions Required)

### 4. Upload Tech Rider Files

The EPK already checks for these files and shows a warning if missing:
- `files/APN_Technische_rider_docx.pdf`
- `files/Technische_Rider_2026.xlsx`

**Steps**:
1. Create the `files/` directory in the repo (if it doesn't exist as a proper folder)
2. Add both files to `files/`
3. Commit and push

### 5. Update Promo Photos

The current promo photos are from 2018. Options:
- **Quick fix**: Take new photos at the next rehearsal with a phone. Portrait and landscape.
- **Better**: Book a photographer for a 30-minute session (can be traded for promotion/credit)
- **Minimum**: Add 2-3 recent live photos to the `photos/` directory and update the HTML

To add a new photo to the grid, add a block like this inside `<div class="photo-grid" id="photoGrid">`:
```html
<div class="photo-card" data-category="promo">
    <img src="https://cdn.jsdelivr.net/gh/allpointsnorthband-art/.github.io@main/photos/NEW_PHOTO_NAME.jpg" alt="Description" loading="lazy">
    <div class="photo-overlay"><div class="photo-overlay-inner"><span class="photo-caption">Promo 2026</span><a href="https://cdn.jsdelivr.net/gh/allpointsnorthband-art/.github.io@main/photos/NEW_PHOTO_NAME.jpg" download="APN-Promo-2026.jpg" class="photo-dl-btn">↓ DL</a></div></div>
</div>
```

### 6. Add Live Show History

The "Upcoming Shows" section currently says "No dates confirmed yet." Add a "Past Shows" section to demonstrate live experience.

Add this block after the "No dates confirmed yet" div:

```html
<h3 style="margin-bottom:16px;">Past Shows</h3>
<div class="table-wrap">
    <table>
        <thead><tr><th>Date</th><th>Venue</th><th>City</th><th>Type</th></tr></thead>
        <tbody>
            <tr><td>2025-XX-XX</td><td>Venue Name</td><td>City</td><td>Headline</td></tr>
            <tr><td>2024-XX-XX</td><td>Venue Name</td><td>City</td><td>Support</td></tr>
            <!-- Add real show history here -->
        </tbody>
    </table>
</div>
```

### 7. Spotify Embed

Already present in the Music section (line ~521 in original). The embed shows the full Embracer EP. No changes needed.

---

## How to Push Changes

```bash
cd /Users/jarno/BMAD/apn-epk
git add -A
git commit -m "Update stats, add newsletter signup section"
git push origin main
```

Changes will be live within 1-2 minutes on GitHub Pages.

---

## Future Enhancements (Nice to Have)

- **SEO meta tags**: Add Open Graph and Twitter Card meta tags for better social sharing
- **Favicon**: Add a favicon (band logo or album art snippet)
- **Google Analytics**: Add GA4 tracking to measure EPK traffic
- **Bandsintown widget**: Embed a Bandsintown widget for automatic show listings
- **Cookie consent**: If adding analytics, add a minimal cookie banner (GDPR)
