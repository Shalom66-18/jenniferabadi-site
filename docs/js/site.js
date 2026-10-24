// Menu, carousel, back-to-top, fade-in. No dependencies.
(function(){
  var t=document.querySelector('.menu-toggle'), n=document.querySelector('.main-nav');
  if(t&&n) t.addEventListener('click',function(){n.classList.toggle('open')});
  document.querySelectorAll('.carousel').forEach(function(c){
    var tr=c.querySelector('.track');
    function step(){var k=tr.querySelector('.card');return k?k.offsetWidth+20:300}
    c.querySelector('.prev').addEventListener('click',function(){tr.scrollBy({left:-step(),behavior:'smooth'})});
    c.querySelector('.next').addEventListener('click',function(){
      if(tr.scrollLeft+tr.clientWidth>=tr.scrollWidth-5) tr.scrollTo({left:0,behavior:'smooth'});
      else tr.scrollBy({left:step(),behavior:'smooth'});
    });
  });
  var top=document.querySelector('.to-top');
  window.addEventListener('scroll',function(){top&&top.classList.toggle('show',scrollY>400)});
  top&&top.addEventListener('click',function(e){e.preventDefault();scrollTo({top:0,behavior:'smooth'})});
  var y=document.querySelector('.site-footer .year'); if(y) y.textContent=new Date().getFullYear();
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12});
    document.querySelectorAll('.reveal').forEach(function(el){io.observe(el)});
  } else document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in')});
})();

// Listings: dropdown / keyword filters + pagination (recipes, articles, class catalog)
(function(){
  document.querySelectorAll('.post-grid[data-paged]').forEach(function(grid){
    var root=grid.closest('.main')||document, per=+grid.dataset.paged, page=1;
    var cards=[].slice.call(grid.querySelectorAll('.post-card')), pager=root.querySelector('.pager');
    var ctrls=[].slice.call(root.querySelectorAll('[data-filter]'));
    function match(c){return ctrls.every(function(f){
      var v=f.value.trim().toLowerCase(); if(!v) return true; var k=f.dataset.filter;
      if(k==='text') return (c.dataset.text||c.textContent.toLowerCase()).indexOf(v)>-1;
      return (c.dataset[k]||'').toLowerCase().split('|').indexOf(v)>-1;})}
    function draw(){
      var shown=cards.filter(match), pages=Math.max(1,Math.ceil(shown.length/per));
      if(page>pages) page=pages;
      cards.forEach(function(c){c.classList.add('hide')});
      shown.slice((page-1)*per,page*per).forEach(function(c){c.classList.remove('hide')});
      var msg=root.querySelector('.empty-msg'); if(!shown.length){if(!msg){msg=document.createElement('p');msg.className='empty-msg';msg.textContent='Nothing found.';grid.after(msg)}}else if(msg) msg.remove();
      if(!pager) return; pager.innerHTML='';
      if(pages<2) return;
      for(var i=1;i<=pages;i++){var b=document.createElement('button');b.textContent=i;if(i===page)b.className='on';
        b.onclick=(function(n){return function(){page=n;draw();grid.scrollIntoView({behavior:'smooth',block:'start'});scrollBy(0,-240)}})(i);pager.appendChild(b)}
    }
    ctrls.forEach(function(f){f.addEventListener(f.tagName==='SELECT'?'change':'input',function(){page=1;draw()})});
    var form=root.querySelector('form.filters'); if(form) form.addEventListener('reset',function(){setTimeout(function(){page=1;draw()},0)});
    draw();
  });
})();

// Share buttons
(function(){
  document.querySelectorAll('.js-share').forEach(function(a){
    a.addEventListener('click',function(e){e.preventDefault();var u=encodeURIComponent(location.href),t=encodeURIComponent(document.title),n=a.dataset.net;
      if(n==='fb') open('https://www.facebook.com/sharer/sharer.php?u='+u,'_blank');
      if(n==='li') open('https://www.linkedin.com/sharing/share-offsite/?url='+u,'_blank');
      if(n==='em') location.href='mailto:?subject='+t+'&body='+u;});
  });
})();

// Contact form: pre-fill from "Message Me About this Class", send without leaving the page
(function(){
  var f=document.querySelector('.contact-form'); if(!f) return;
  var cls=new URLSearchParams(location.search).get('class');
  if(cls){var m=f.querySelector('textarea');m.value='I am interested in the class: '+cls+'\n\n';
    var c=f.querySelector('input[value="Cooking Class/Demonstration"]'); if(c) c.checked=true;}
  f.addEventListener('submit',function(e){
    var st=f.querySelector('.form-status'); e.preventDefault();
    if(!f.querySelector('input[name="interests[]"]:checked')){st.hidden=false;st.className='form-status error';st.textContent='Please choose at least one interest.';return}
    // Newsletter box ticked: subscribe to Jennifer's Mailchimp list (Mailchimp emails them to confirm)
    var nl=f.querySelector('input[name="newsletter"]');
    if(nl&&nl.checked&&f.dataset.mailchimp){
      var cb='mc'+Date.now(), q='&EMAIL='+encodeURIComponent(f.email.value)+'&FNAME='+encodeURIComponent(f.first_name.value)+'&LNAME='+encodeURIComponent(f.last_name.value);
      window[cb]=function(){delete window[cb]};
      var sc=document.createElement('script'); sc.src=f.dataset.mailchimp+q+'&c='+cb; document.body.appendChild(sc);
    }
    var data=new FormData(f), interests=data.getAll('interests[]'); data.delete('interests[]'); data.append('interests',interests.join(', '));
    st.hidden=false;st.className='form-status';st.textContent='Sending…';
    fetch(f.action,{method:'POST',body:data,headers:{Accept:'application/json'}}).then(function(r){return r.json()}).then(function(j){
      if(j.success){f.reset();st.textContent='Thank you! Your message has been sent. Jennifer will get back to you soon.'}
      else throw 0;}).catch(function(){st.className='form-status error';st.textContent='Sorry, the message could not be sent. Please try again later.'});
  });
})();
