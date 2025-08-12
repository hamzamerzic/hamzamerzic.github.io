---
layout: post
title: EEML 2025 Wrap Up!
date: 2025-08-08 16:00:00
description: BTS on Eastern European Machine Learning Summer School in Sarajevo.
thumbnail: assets/img/eeml/eeml participants.jpeg
categories: general
giscus_comments: true
related_posts: false
---

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>

<style>
  .swiper {
    max-width: 720px;
    margin: 2rem auto;
    border-radius: 0.75rem;
    overflow: hidden;
  }
  .swiper-slide {
    aspect-ratio: 4 / 3;
    background: var(--global-bg-color);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .swiper-slide img {
    width: 100%;
    height: 100%;
    display: block;
  }
  .img-cover img {
    object-fit: cover;
  }
  .img-contain img {
    object-fit: contain;
  }
  .swiper-button-prev,
  .swiper-button-next {
    color: var(--global-theme-color);
    opacity: 0.4;
    transition: opacity 0.3s ease;
  }
  .swiper-button-prev:hover,
  .swiper-button-next:hover {
    opacity: 1;
  }
  .swiper-pagination-bullet-active {
    background: var(--global-theme-color);
  }
</style>

## Bringing EEML to Sarajevo: A story about chairs, ćevapi, and controlled chaos

It’s been a couple of weeks now since the [Eastern European Machine Learning Summer School](https://www.eeml.eu) wrapped up in Sarajevo. I’ve had some time to unwind, reacquaint myself with the concept of a full night's sleep, and finally try to put into words what was, frankly, one of the most insane and deeply rewarding projects of my life.

Bringing a major academic event like EEML to Bosnia had been a quiet dream of mine for quite a while. I remember seeing an internal DeepMind post (back when we used Slack) about EEML around seven years ago and I immediately thought how amazing for the local ecosystem it would be to have something like this in Bosnia. A few years prior, I had co-founded the [Association for Advancement of Science and Technology](https://www.annt.ba) (ANNT in Bosnian) and organizing a major science conference was something we were slowly building toward as it aligned perfectly with our mission. We started from the ground up, founding a local yearly [STEM youth camp](https://annt.ba/stem-youth-camp/) and growing it to host around 80 college students. And to be completely honest, I thought it would take us a long time to grow our youth camp to something as big as EEML.

Even when I joined the EEML team last year in Serbia, hosting in Bosnia felt like a distant goal. Then, as things happen, I ended up stepping in and taking over the reinforcement learning keynote last-minute. It went surprisingly well and gave me a little bit of an aura that, in hindsight, likely played a part in bringing EEML to Bosnia this year.

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/eeml2024.jpeg' | relative_url }}" alt="The official design for EEML 2024 in Novi Sad, Serbia." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/eeml2024lectureslides.png' | relative_url }}" alt="A slide from the author's reinforcement learning presentation at EEML 2024." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/eeml2024lecture.jpg' | relative_url }}" alt="The author standing at a podium giving a reinforcement learning lecture at EEML 2024." loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>
<div class="caption mt-2">
  Flashback to EEML 2024 in Serbia, where the idea for Sarajevo first gained momentum.
</div>

## The gentle art of persuasion

After returning from last year’s EEML in August, I still had no idea that there was a chance for EEML to happen in Bosnia so soon. The general rule for EEML was that a country would host a short, 1-2 day workshop a year prior, so the core organizers could meet the local team and test the waters. First discussions started in November and organizing EEML in Croatia seemed like the natural next step as Matko had been part of EEML for a few years and they already held an EEML workshop in Zagreb. But, Matko was in parallel working to bring the [Mediteranean Machine Learning Summer School](https://www.m2lschool.org/) (M2L) to Croatia and since that worked out, all of a sudden EEML 2025 was on the table for Bosnia. The local team from ANNT was super excited, but we had to show the core EEML team that we (since I’m the only local non-local organizer 😅) could handle the logistics from scratch. We had to prove that we could sort out the accommodation, venue, and food for around 250 people (at the time 😆), and that there was enough local interest to make it successful but also bring value to the local community through their engagement.

We made our case, and somehow, it was convincing enough so we got the green light in December and my entire last year changed overnight! It was full power from that moment on.

In hindsight, I do have to admit that I might have overestimated the local community's readiness a little. With ANNT, we had just finished a project to map out the [AI landscape](https://annt.ba/predstavljamo-ai-landscape-bosne-i-herzegovine-24/) in Bosnia, and on paper, it looked like a lot was happening. The reality was a bit quieter, but we still managed to bring out the best out of the local community.

## The great venue puzzle

The minute we started planning, we hit our first big Sarajevo-specific problem, starting with the accommodation. In the past, EEML participants were usually housed in student dorms, but the dorms in Sarajevo generally don't have A/C, which was out of the question for a summer school in July. This forced us to look elsewhere and we narrowed our choice down to two hotels.

We had to consider the trade-off: one outside of the city and the other more expensive at the heart of it all. This choice added to the overall complexity and cost of the organization, but we decided that being a walking distance from the city center would provide a much better experience for everyone. We chose one of Bosnia's most iconic hotels, built for the 1984 Winter Olympics. Of course, this was much pricier for us as we subsidized the costs heavily to keep things affordable for the participants.

With the accommodation sorted, the next puzzle was the lecture venue. There is one lecture hall at the university's mechanical engineering faculty that was big enough, but it also didn't have A/C. So, we made another big decision: to host the lectures at the same hotel. It was more expensive and meant we had to figure out how to turn a conference hall into a proper lecture theatre, but it simplified the logistics slightly and created a better, more integrated experience. This was a first for EEML, having students and lecture under one roof in a hotel.

The decision to go all-in on a pricier hotel and subsidize the accommodation had a cascade effect. It meant we needed more sponsors. But EEML is not a conference where you can just buy a seat; it’s a prestigious academic event with an acceptance rate of around 20%, based on academic excellence and we carefully curate both participants and sponsors to provide the best value for everyone. So to keep the balance healthy, for every sponsor we added, we also had to accept more students, which, in turn, increased our logistical complexity and costs even further. It's a delicate balance that can quickly turn into a deadly loop. Our initial goal of 250 participants ballooned to 350, making **EEML 2025 the largest in-person one to date**, with participants from around 50 countries joining us in Sarajevo.

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/tshirts and chairs.jpg' | relative_url }}" alt="A stack of EEML 2025 T-shirts next to rows of lecture chairs with fold-out tables." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/locations.png' | relative_url }}" alt="A map of Sarajevo showing the key choices for the EEML 2025 summer school." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/mef.jpg' | relative_url }}" alt= "The large lecture hall of the Mechanical Engineering Faculty building, a potential venue for the school." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/holiday_sarajevo.jpg' | relative_url }}" alt="The exterior of the iconic Hotel Holiday in Sarajevo, the chosen venue for EEML 2025." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/chairs.png' | relative_url }}" alt="The chairs with fold-out tables that we found at SSST." loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>
<div class="caption mt-2">
  The planning phase: choosing locations, hunting for chairs, and final preparations.
</div>

## Top three logistical nightmares

As the planning intensified, a few key worries kept me up at night.

- **The Food:** How do you feed 350 people, three times a day, on a budget, without just serving them dry sandwiches? Here, our friends at [Zmaj](https://zmajcevabdzinica.ba/), a fantastic local restaurant, became our unsung heroes. They’re famous for their ćevapi and meat-heavy dishes, but they completely transformed their operation just for us. They closed off the main part of their restaurant for the week, worked practically without profit, and cooked whatever we needed. Their support was just incredible.
- **The Chairs:** This one still makes me laugh. The hotel’s conference hall was big, but their table setup only fit 250 people with poor visibility. We needed chairs with those little fold-out laptop tables. After searching all over the city, we found exactly one institution that had them in the quantity we needed: the [Sarajevo School of Science and Technology](https://ssst.edu.ba/en) (SSST). They graciously lent us over 350 of them. The catch? We had to transport them ourselves. This involved two trucks and our team personally loading and unloading every single chair. Twice. To add a perfect, chaotic cherry on top, on the return journey, a car crashed into one of our trucks, blocking traffic on a busy street for nearly two hours. You just can’t make this stuff up.
- **The Internet:** Anyone who has run a technical workshop knows that bad Wi-Fi can ruin everything. We were especially paranoid because the tutorials required students to download model weights, and the hotel's internet had a questionable reputation. Thankfully, our platinum sponsor, [BH Telecom](https://www.bhtelecom.ba/), stepped in and became our saviors. They installed a dedicated high-bandwidth line just for the event. We still had a few hiccups on day one, so we also had the hotel max out their own provider's bandwidth. With two networks running in parallel, we were finally safe.

## Going the extra mile (sometimes literally)

Beyond the big three, there was a mountain of smaller, absurd challenges. Renting poster stands was almost the same price as buying them, so we bought our own. Then there was the construction site that popped up right in front of the hotel. We had to be on top of them constantly, especially when they started using a machine that was literally shaking the whole hotel. Of course, this happened during one of our most anticipated lectures, and we had to promptly call the owners to get them to stop the works.

But we also tried to add touches that went beyond just running the program. We wanted participants to feel looked after from the moment they landed, in the true spirit of Eastern European hospitality. This led to one of the biggest organizational hurdles: picking up every single participant from the airport. It was a massive effort, and yes, even I was taxiing people around, haha. On top of that, we were dealing with a constant stream of small issues, like the A/C failing in a tutorial room, which our team would immediately jump on. It was these small interventions that helped make the week run smoothly.

The week itself was action-packed with daily lectures, tutorials, and a packed social schedule with welcome drinks, poster sessions, and a gala dinner. Thursday was usually a half-day off, but this year we decided to organize a trip to the Tunnel of Salvation museum and a guided city tour. The day was further enriched by a brilliant Estimathon competition organized by [Jane Street](https://www.janestreet.com/) and evening drinks hosted by [Credo VC](https://www.credoventures.com/). While the participants networked, the organizers, speakers, and TAs snuck off for a quiet dinner—our well deserved moment of calm.

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/suad rector president and I.jpg' | relative_url }}" alt="The author pictured with local dignitaries, including a university rector and an association president." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/viorica organizing team.jpg' | relative_url }}" alt="Viorica's opening slide showing the organizing team members." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/speakers and topics.jpg' | relative_url }}" alt="The author's slide introducing the speakers and their corresponding topics." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/organizers and volunteers.jpg' | relative_url }}" alt="The (almost) full team of EEML 2025 organizers and volunteers smiling together." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/ferenc.jpg' | relative_url }}" alt="Speaker Ferenc Huszár giving his Intro to Deep Learning lecture to a full audience at EEML 2025." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/tutorial.jpg' | relative_url }}" alt="Participants working on their laptops during a hands-on tutorial session." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/welcome drinks.jpg' | relative_url }}" alt="Attendees mingling and networking during the welcome drinks reception." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/spica.jpg' | relative_url }}" alt="Participants in the bar area of the poster session." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/posters.jpg' | relative_url }}" alt="Attendees discussing research during the EEML 2025 poster session." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/panel.JPG' | relative_url }}" alt="A panel of speakers on stage answering questions from the audience." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/estimathon.jpg' | relative_url }}" alt="Participants collaborating in teams during the Jane Street Estimathon competition." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/speaker_dinner.jpg' | relative_url }}" alt="The speakers, organizers, and TAs enjoying a quiet dinner together." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/gala dinner.jpg' | relative_url }}" alt="A view from the EEML 2025 gala dinner." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/certificates.JPG' | relative_url }}" alt="The organizing team awarding certificates of appreciation at the end of the school." loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>
<div class="caption mt-2">
  A snapshot of the action-packed EEML week.
</div>

The last day was shorter, with final lectures and student project presentations. We handed out certificates, including the much-anticipated **best meme award**, and had to wrap things up a bit sharpish as the hotel had a massive wedding booked for that evening.

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/best memes award.jpg' | relative_url }}" alt="The organizing team awarding the best meme award." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/president.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/lanyards.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/lectures.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/questions.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/lobby music.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/zmaj.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/ice cream.jpg' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/ice cream 2.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/poster.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/razvan.jpg' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/wifi.jpg' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/road to gala dinner.jpg' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/sgd.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/cevapi.jpg' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/headache.png' | relative_url }}" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/adna.png' | relative_url }}" alt="Old site blog" loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/memes/end of eeml.jpg' | relative_url }}" alt="Old site blog" loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>
<div class="caption mt-2">
  Memez!
</div>

## The aftermath

Hosting around 350 people from around 50 countries in my hometown was surreal. I'm so incredibly proud to witness ANNT grow from a handful of science enthusiasts into an association capable of successfully organizing a 350-person international event. I feel so happy to be part of a community that made an event like this a huge pleasure for everyone who attended and presented our country in the best light. We heard from so many people how they can't wait to be back, and from some, how it was a life-changing event. That’s the best we could have ever hoped for.

Of course, this would have been completely impossible without the army of people who helped make it happen. A huge thank you to:

- The **core EEML team** for bringing everyone together and for their passion in fulfilling EEML's mission.
- The amazing **speakers**, **tutorial leads**, and **teaching assistants** who shared their invaluable knowledge and time.
- The entire **ANNT** team and our **volunteers**, who did so much of the heavy lifting and went the extra mile to make sure everything ran smoothly.
- Our **sponsors**, whose continued financial support is making EEML possible.
- **BH Telecom**, **SSST**, and **Zmaj**, for stepping up to help solve some of our main logistical challenges.
- The many **Friends and Supporters** who provided help along the way, especially [SO.. quantum marketing agency](https://so.agency/), for the great work with the media outreach.
- The **participants** for bringing their questions, enthusiasm, memes, and the energy that makes every EEML so special.

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/eeml participants.jpeg' | relative_url }}" alt="A large group photo of all the EEML 2025 participants." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/organizers with certificates.JPG' | relative_url }}" alt="The main organizers smiling and holding their certificates of appreciation." loading="lazy" />
    </div>
    <div class="swiper-slide img-cover">
      <img src="{{ '/assets/img/eeml/gdm org team.jpg' | relative_url }}" alt="A photo of the author with the core Google DeepMind organizing team." loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>
<div class="caption mt-2">
  Final day of EEML.
</div>

This last year was not what I had in mind a year ago. But I like to say that most often we don't get what we plan for, but with the right mindset, we get rewarded with much more. And this experience was certainly that.

<div class="swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/eeml landing.png' | relative_url }}" alt="The official landing page graphic for EEML 2025 in Sarajevo, Bosnia and Herzegovina." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/Sarajevo panorama.jpg' | relative_url }}" alt="A beautiful panoramic view of the city of Sarajevo." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/sebilj.jpeg' | relative_url }}" alt="A photo of the iconic Sebilj wooden fountain in Sarajevo's Baščaršija old town with the EEML logo." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/country of origin.jpg' | relative_url }}" alt="Pie chart showing the breakdown of EEML 2025 participants by country of origin." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/education level.jpg' | relative_url }}" alt="Bar chart showing the educational background of participants (e.g., PhD, Masters, undergrad)." loading="lazy" />
    </div>
    <div class="swiper-slide img-contain">
      <img src="{{ '/assets/img/eeml/gender identity.jpg' | relative_url }}" alt="Pie chart showing the gender identity breakdown of EEML 2025 participants." loading="lazy" />
    </div>
  </div>
  <div class="swiper-button-next"></div>
  <div class="swiper-button-prev"></div>
  <div class="swiper-pagination"></div>
</div>
<div class="caption mt-2">
  EEML 2025 in visuals.
</div>

I've tried to capture a small fraction of my EEML 2025 story here, but there were 350 other stories unfolding that week. I’d love to hear yours! **If you have a favorite memory please share it in the comments below.**

And if bringing science and technology communities together is something you're passionate about or you'd like to get inolved with ANNT, please don't hesitate to get in touch!

<script>
  document.querySelectorAll('.swiper').forEach((swiperEl) => {
    new Swiper(swiperEl, {
      loop: true,
      spaceBetween: 16,
      pagination: {
        el: swiperEl.querySelector('.swiper-pagination'),
        clickable: true,
      },
      navigation: {
        nextEl: swiperEl.querySelector('.swiper-button-next'),
        prevEl: swiperEl.querySelector('.swiper-button-prev'),
      },
    });
  });
</script>
