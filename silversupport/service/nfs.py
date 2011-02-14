

<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <title>
	cuu508 / silverlining / source – Bitbucket
</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta name="description" content="" />
  <meta name="keywords" content="cuu508,NFS,service,and,misc.,messing,around,source,sourcecode,silversupport/service/nfs.py@eb9a9c749925" />

  <link rel="stylesheet" href="https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/css/0c8bf63f4b84.css" type="text/css">
<link rel="stylesheet" href="https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/css/05d92c3c7951.css" type="text/css" media="print">


  <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="Bitbucket" />
  <link rel="icon" href="https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/img/logo_new.png" type="image/png" />

  <!--[if IE]>
  <script src="https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/js/lib/excanvas.js"></script>
  <![endif]-->

  <script type="text/javascript">var MEDIA_URL = "https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/";</script>
  <script type="text/javascript">
    (function () {

      window.BB || (window.BB = {});
      window.BB.user || (window.BB.user = {});
      window.BB.repo || (window.BB.repo = {});

    

    
      window.BB.repo.slug = 'silverlining';
    

    
      window.BB.repo.owner = {
        username: 'cuu508'
      };
    
    }());
  </script>

  


  <script src="https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/js/lib/bundle.js"></script>



	<link rel="stylesheet" href="https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/css/highlight/trac.css" type="text/css" />


</head>

<body class="">

  <div id="wrapper">



  <div id="header-wrap">
    <div id="header">
    <ul id="global-nav">
      <li><a class="home" href="http://www.atlassian.com">Atlassian Home</a></li>
      <li><a class="docs" href="http://confluence.atlassian.com/display/BITBUCKET">Documentation</a></li>
      <li><a class="support" href="/support">Support</a></li>
      <li><a class="blog" href="http://blog.bitbucket.org">Blog</a></li>
      <li><a class="forums" href="http://groups.google.com/group/bitbucket-users">Forums</a></li>
    </ul>
    <a href="/" id="logo">Bitbucket by Atlassian</a>

    <div id="main-nav" class="clearfix">
    
      <ul class="clearfix">
        <li><a href="/plans">Pricing &amp; Signup</a></li>
        <li><a href="/repo/month">Explore Bitbucket</a></li>
        <li><a href="/account/signin/">Log in</a></li>
        

<li class="search-box">
  <form action="/repo/all">
    <input type="text" name="name" id="search" placeholder="Find a project" />
  </form>
</li>

      </ul>
    
    </div>
    </div>
  </div>

    <div id="header-messages">
  
  
    
    
    
    
  

    
   </div>



    <div id="content">
      
	
  





  <script type="text/javascript">
    jQuery(function ($) {
        var cookie = $.cookie,
            cookieOptions, date,
            $content = $('#content'),
            $pane = $('#what-is-bitbucket'),
            $hide = $pane.find('[href="#hide"]').css('display', 'block').hide();

        date = new Date();
        date.setTime(date.getTime() + 365 * 24 * 60 * 60 * 1000);
        cookieOptions = { path: '/', expires: date };

        if (cookie('toggle_status') == 'hide') $content.addClass('repo-desc-hidden');

        $('#toggle-repo-content').click(function (event) {
            event.preventDefault();
            $content.toggleClass('repo-desc-hidden');
            cookie('toggle_status', cookie('toggle_status') == 'show' ? 'hide' : 'show', cookieOptions);
        });

        if (!cookie('hide_intro_message')) $pane.show();

        $hide.click(function (event) {
            event.preventDefault();
            cookie('hide_intro_message', true, cookieOptions);
            $pane.slideUp('slow');
        });

        $pane.hover(
            function () { $hide.fadeIn('fast'); },
            function () { $hide.fadeOut('fast'); });
    });
  </script>



  
  
  
  
  
    <div id="what-is-bitbucket" class="new-to-bitbucket">
      <h2>Pēteris Caune <span id="slogan">is sharing code with you</span></h2>
      <img src="https://bitbucket-assetroot.s3.amazonaws.com:443/c/photos/2011/Jan/25/cuu508-avatar-2787505205-1_avatar.jpg" alt="" class="avatar" />
      <p>Bitbucket is a code hosting site. Unlimited public and private repositories. Free for small teams.</p>
      <div class="primary-action-link signup"><a href="/account/signup/?utm_source=internal&utm_medium=banner&utm_campaign=what_is_bitbucket">Try Bitbucket free</a></div>
      <a href="#hide" title="Don't show this again">Don't show this again</a>
    </div>
  


<div id="tabs">
  <ul class="tabs">
    <li>
      <a href="/cuu508/silverlining/overview">Overview</a>
    </li>

    <li>
      <a href="/cuu508/silverlining/downloads">Downloads (0)</a>
    </li>

    

    

    <li class="selected">
      
        <a href="/cuu508/silverlining/src/eb9a9c749925">Source</a>
      
    </li>

    <li>
      <a href="/cuu508/silverlining/changesets">Changesets</a>
    </li>

    

    

    

    <li class="secondary">
      <a href="/cuu508/silverlining/descendants">Forks/Queues (0)</a>
    </li>

    <li class="secondary">
      <a href="/cuu508/silverlining/zealots">Followers (<span id="followers-count">0</span>)</a>
    </li>
  </ul>
</div>

  <div class="repo-menu" id="repo-menu">
    <ul id="repo-menu-links">
     
      <li>
        <a href="/cuu508/silverlining/rss" class="rss" title="RSS feed for silverlining">RSS</a>
      </li>
      <li>
        <a href="/cuu508/silverlining/atom" class="atom" title="Atom feed for silverlining">Atom</a>
      </li>
      
        <li>
          <a href="/cuu508/silverlining/pull" class="pull-request">
            pull request
          </a>
        </li>
      
      <li><a href="/cuu508/silverlining/fork" class="fork">fork</a></li>
      
        <li><a href="/cuu508/silverlining/hack" class="patch-queue">patch queue</a></li>
      
      <li>
        <a rel="nofollow" href="/cuu508/silverlining/follow" class="follow">follow</a>
      </li>
      
        <li>
          <a class="source">get source</a>
          <ul class="downloads">
            
              <li><a rel="nofollow" href="/cuu508/silverlining/get/eb9a9c749925.zip">zip</a></li>
              <li><a rel="nofollow" href="/cuu508/silverlining/get/eb9a9c749925.tar.gz">gz</a></li>
              <li><a rel="nofollow" href="/cuu508/silverlining/get/eb9a9c749925.tar.bz2">bz2</a></li>
            
          </ul>
        </li>
      
    </ul>

  
    <ul class="metadata">
    
      <li class="branches">branches
        <ul>
          <li><a href="/cuu508/silverlining/src/42bdb173a7fe">trunk</a>
               <a class='menu-compare' href="/cuu508/silverlining/compare/default..trunk" title="Show changes between trunk and default"><img src="https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/img/arrow_switch.png"/></a></li>
          <li><a href="/cuu508/silverlining/src/eb9a9c749925">default</a>
              </li>
        </ul>
      </li>
    
      <li class="tags">tags
        <ul>
          <li><a href="/cuu508/silverlining/src/eb9a9c749925">tip</a>
            </li>
        </ul>
      </li>
    </ul>
  
</div>
<div class="repo-menu" id="repo-desc">
  

    <ul id="repo-menu-links-mini">
      
      <li>
        <a href="/cuu508/silverlining/rss" class="rss" title="RSS feed for silverlining"></a>
      </li>
      <li>
        <a href="/cuu508/silverlining/atom" class="atom" title="Atom feed for silverlining"></a>
      </li>
      
        <li>
          <a href="/cuu508/silverlining/pull" class="pull-request" title="Pull request"></a>
        </li>
      
      <li><a href="/cuu508/silverlining/fork" class="fork" title="Fork"></a></li>
      
        <li><a href="/cuu508/silverlining/hack" class="patch-queue" title="Patch queue"></a></li>
      
      <li>
        <a rel="nofollow" href="/cuu508/silverlining/follow" class="follow">follow</a>
      </li>
      
        <li>
          <a class="source" title="Get source"></a>
          <ul class="downloads">
            
              <li><a rel="nofollow" href="/cuu508/silverlining/get/eb9a9c749925.zip">zip</a></li>
              <li><a rel="nofollow" href="/cuu508/silverlining/get/eb9a9c749925.tar.gz">gz</a></li>
              <li><a rel="nofollow" href="/cuu508/silverlining/get/eb9a9c749925.tar.bz2">bz2</a></li>
            
          </ul>
        </li>
      
    </ul>

    <h3 id="repo-heading">
      <a href="/cuu508">cuu508</a> /
      <a href="/cuu508/silverlining">silverlining</a>
    
      (fork of <a href="/ianb/silverlining/src">silverlining</a>
      <a class="compare-link" href="/cuu508/silverlining/compare/default..ianb/silverlining" title="Show changes between silverlining and silverlining"><img src="https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/img/arrow_switch.png"/></a>)
    
    </h3>

  <p class="repo-desc-description">NFS service and misc. messing around</p>

  <div id="repo-desc-cloneinfo">Clone this repository (size: 945.9 KB): <a href="https://bitbucket.org/cuu508/silverlining" onclick="$('#clone-url-ssh').hide();$('#clone-url-https').toggle();return(false);"><small>HTTPS</small></a> / <a href="ssh://hg@bitbucket.org/cuu508/silverlining" onclick="$('#clone-url-https').hide();$('#clone-url-ssh').toggle();return(false);"><small>SSH</small></a><br />
    <pre id="clone-url-https">hg clone <a href="https://bitbucket.org/cuu508/silverlining">https://bitbucket.org/cuu508/silverlining</a></pre>

    <pre id="clone-url-ssh" style="display:none;">hg clone <a href="ssh://hg@bitbucket.org/cuu508/silverlining">ssh://hg@bitbucket.org/cuu508/silverlining</a></pre></div>

  <a href="#" id="toggle-repo-content"></a>

  

</div>



      

<div id="source-path" class="layout-box">
	<a href="/cuu508/silverlining/src">silverlining</a> /
	
		
			
				<a href="/cuu508/silverlining/src/eb9a9c749925/silversupport/">
					silversupport
				</a>
			
		
		/
	
		
			
				<a href="/cuu508/silverlining/src/eb9a9c749925/silversupport/service/">
					service
				</a>
			
		
		/
	
		
			
				nfs.py
			
		
		
	
</div>


<div id="source-view">
	<table class="info-table">
		<tr>
			<th>r523:eb9a9c749925</th>
			<th>50 loc</th>
			<th>1.4 KB</th>
			<th class="source-view-links">
				<a id="embed-link" href="#" onclick="makeEmbed('#embed-link', 'https://bitbucket.org/cuu508/silverlining/src/eb9a9c749925/silversupport/service/nfs.py?embed=t');">embed</a> /
				<a href="/cuu508/silverlining/history/silversupport/service/nfs.py">history</a> /
				<a href="/cuu508/silverlining/annotate/eb9a9c749925/silversupport/service/nfs.py">annotate</a> /
				<a href="/cuu508/silverlining/raw/eb9a9c749925/silversupport/service/nfs.py">raw</a> /
				<form action="/cuu508/silverlining/diff/silversupport/service/nfs.py" class="source-view-form">
					
					<input type="hidden" name="diff2" value="eb9a9c749925" />
						<select name="diff1" class="smaller">
							
								
									<option value="76090728f447">
										r503:76090728f447
									</option>
								
							
								
									<option value="8113e727736f">
										r487:8113e727736f
									</option>
								
							
								
									<option value="5ea8ae47b3dd">
										r486:5ea8ae47b3dd
									</option>
								
							
						</select>
						<input type="submit" value="diff" class="smaller" />
					
				</form>
			</th>
		</tr>
	</table>
	
		<div class="scroll-x">
		
			<table class="highlighttable"><tr><td class="linenos"><div class="linenodiv"><pre><a href="#cl-1"> 1</a>
<a href="#cl-2"> 2</a>
<a href="#cl-3"> 3</a>
<a href="#cl-4"> 4</a>
<a href="#cl-5"> 5</a>
<a href="#cl-6"> 6</a>
<a href="#cl-7"> 7</a>
<a href="#cl-8"> 8</a>
<a href="#cl-9"> 9</a>
<a href="#cl-10">10</a>
<a href="#cl-11">11</a>
<a href="#cl-12">12</a>
<a href="#cl-13">13</a>
<a href="#cl-14">14</a>
<a href="#cl-15">15</a>
<a href="#cl-16">16</a>
<a href="#cl-17">17</a>
<a href="#cl-18">18</a>
<a href="#cl-19">19</a>
<a href="#cl-20">20</a>
<a href="#cl-21">21</a>
<a href="#cl-22">22</a>
<a href="#cl-23">23</a>
<a href="#cl-24">24</a>
<a href="#cl-25">25</a>
<a href="#cl-26">26</a>
<a href="#cl-27">27</a>
<a href="#cl-28">28</a>
<a href="#cl-29">29</a>
<a href="#cl-30">30</a>
<a href="#cl-31">31</a>
<a href="#cl-32">32</a>
<a href="#cl-33">33</a>
<a href="#cl-34">34</a>
<a href="#cl-35">35</a>
<a href="#cl-36">36</a>
<a href="#cl-37">37</a>
<a href="#cl-38">38</a>
<a href="#cl-39">39</a>
<a href="#cl-40">40</a>
<a href="#cl-41">41</a>
<a href="#cl-42">42</a>
<a href="#cl-43">43</a>
<a href="#cl-44">44</a>
<a href="#cl-45">45</a>
<a href="#cl-46">46</a>
<a href="#cl-47">47</a>
<a href="#cl-48">48</a>
<a href="#cl-49">49</a>
<a href="#cl-50">50</a>
</pre></div></td><td class="code"><div class="highlight"><pre><a name="cl-1"></a><span class="sd">&quot;&quot;&quot;NFS service support&quot;&quot;&quot;</span>
<a name="cl-2"></a>
<a name="cl-3"></a><span class="kn">import</span> <span class="nn">os</span>
<a name="cl-4"></a><span class="kn">import</span> <span class="nn">pwd</span>
<a name="cl-5"></a><span class="kn">import</span> <span class="nn">grp</span>
<a name="cl-6"></a>
<a name="cl-7"></a><span class="kn">from</span> <span class="nn">silversupport.shell</span> <span class="kn">import</span> <span class="n">run</span>
<a name="cl-8"></a><span class="kn">from</span> <span class="nn">silversupport.abstractservice</span> <span class="kn">import</span> <span class="n">AbstractService</span>
<a name="cl-9"></a>
<a name="cl-10"></a>
<a name="cl-11"></a><span class="k">class</span> <span class="nc">Service</span><span class="p">(</span><span class="n">AbstractService</span><span class="p">):</span>
<a name="cl-12"></a>
<a name="cl-13"></a>    <span class="n">packages</span> <span class="o">=</span> <span class="p">[</span><span class="s">&quot;nfs-common&quot;</span><span class="p">]</span>
<a name="cl-14"></a>    <span class="n">platform_packages</span> <span class="o">=</span> <span class="p">{}</span>
<a name="cl-15"></a>    <span class="n">root</span> <span class="o">=</span> <span class="s">&#39;/var/lib/silverlining/apps&#39;</span>
<a name="cl-16"></a>
<a name="cl-17"></a>    <span class="nd">@property</span>
<a name="cl-18"></a>    <span class="k">def</span> <span class="nf">local_dir</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span>
<a name="cl-19"></a>        <span class="k">return</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">root</span><span class="p">,</span> <span class="bp">self</span><span class="o">.</span><span class="n">app_config</span><span class="o">.</span><span class="n">app_name</span> <span class="o">+</span> <span class="s">&quot;_nfs_share&quot;</span><span class="p">)</span>
<a name="cl-20"></a>
<a name="cl-21"></a>    <span class="k">def</span> <span class="nf">install</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span>
<a name="cl-22"></a>        <span class="bp">self</span><span class="o">.</span><span class="n">install_packages</span><span class="p">()</span>
<a name="cl-23"></a>        
<a name="cl-24"></a>        <span class="k">if</span> <span class="ow">not</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">exists</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">local_dir</span><span class="p">):</span>
<a name="cl-25"></a>            <span class="n">os</span><span class="o">.</span><span class="n">makedirs</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">local_dir</span><span class="p">)</span>
<a name="cl-26"></a>
<a name="cl-27"></a>            <span class="n">uid</span> <span class="o">=</span> <span class="n">pwd</span><span class="o">.</span><span class="n">getpwnam</span><span class="p">(</span><span class="s">&#39;www-data&#39;</span><span class="p">)</span><span class="o">.</span><span class="n">pw_uid</span>
<a name="cl-28"></a>            <span class="n">gid</span> <span class="o">=</span> <span class="n">grp</span><span class="o">.</span><span class="n">getgrnam</span><span class="p">(</span><span class="s">&#39;www-data&#39;</span><span class="p">)</span><span class="o">.</span><span class="n">gr_gid</span>
<a name="cl-29"></a>            <span class="n">os</span><span class="o">.</span><span class="n">chown</span><span class="p">(</span><span class="bp">self</span><span class="o">.</span><span class="n">local_dir</span><span class="p">,</span> <span class="n">uid</span><span class="p">,</span> <span class="n">gid</span><span class="p">)</span>
<a name="cl-30"></a>            
<a name="cl-31"></a>        <span class="n">remote_dir</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">config_string</span>
<a name="cl-32"></a>        
<a name="cl-33"></a>        <span class="c"># Update /etc/fstab with new entry</span>
<a name="cl-34"></a>        <span class="k">if</span> <span class="ow">not</span> <span class="n">remote_dir</span> <span class="ow">in</span> <span class="nb">open</span><span class="p">(</span><span class="s">&quot;/etc/fstab&quot;</span><span class="p">)</span><span class="o">.</span><span class="n">read</span><span class="p">():</span>
<a name="cl-35"></a>            <span class="n">fstab_line</span> <span class="o">=</span> <span class="s">&quot;</span><span class="se">\n</span><span class="si">%s</span><span class="s"> </span><span class="si">%s</span><span class="s"> nfs4 proto=tcp,port=2049 0 0</span><span class="se">\n</span><span class="s">&quot;</span> <span class="o">%</span> \
<a name="cl-36"></a>                <span class="p">(</span><span class="n">remote_dir</span><span class="p">,</span> <span class="bp">self</span><span class="o">.</span><span class="n">local_dir</span><span class="p">)</span>
<a name="cl-37"></a>            
<a name="cl-38"></a>            <span class="n">fstab_file</span> <span class="o">=</span> <span class="nb">open</span><span class="p">(</span><span class="s">&quot;/etc/fstab&quot;</span><span class="p">,</span> <span class="s">&quot;a&quot;</span><span class="p">)</span>
<a name="cl-39"></a>            <span class="n">fstab_file</span><span class="o">.</span><span class="n">write</span><span class="p">(</span><span class="n">fstab_line</span><span class="p">)</span>
<a name="cl-40"></a>            <span class="n">fstab_file</span><span class="o">.</span><span class="n">close</span><span class="p">()</span>
<a name="cl-41"></a>        
<a name="cl-42"></a>        <span class="c"># Mount it if not already mounted </span>
<a name="cl-43"></a>        <span class="n">_</span><span class="p">,</span> <span class="n">_</span><span class="p">,</span> <span class="n">not_mounted</span> <span class="o">=</span> <span class="n">run</span><span class="p">([</span><span class="s">&quot;mountpoint&quot;</span><span class="p">,</span> <span class="s">&quot;-q&quot;</span><span class="p">,</span> <span class="bp">self</span><span class="o">.</span><span class="n">local_dir</span><span class="p">])</span>
<a name="cl-44"></a>        <span class="k">if</span> <span class="n">not_mounted</span><span class="p">:</span>
<a name="cl-45"></a>            <span class="n">run</span><span class="p">([</span><span class="s">&#39;mount&#39;</span><span class="p">,</span> <span class="bp">self</span><span class="o">.</span><span class="n">local_dir</span><span class="p">])</span>
<a name="cl-46"></a>
<a name="cl-47"></a>    <span class="k">def</span> <span class="nf">env_setup</span><span class="p">(</span><span class="bp">self</span><span class="p">):</span>
<a name="cl-48"></a>        <span class="n">environ</span> <span class="o">=</span> <span class="p">{}</span>
<a name="cl-49"></a>        <span class="n">environ</span><span class="p">[</span><span class="s">&#39;CONFIG_NFS_DIR&#39;</span><span class="p">]</span> <span class="o">=</span> <span class="bp">self</span><span class="o">.</span><span class="n">local_dir</span>
<a name="cl-50"></a>        <span class="k">return</span> <span class="n">environ</span>
</pre></div>
</td></tr></table>
		
		</div>
	
</div>



    </div>

  </div>

  <div id="footer">
    <ul id="footer-nav">
      <li>Copyright © 2011 <a href="http://atlassian.com">Atlassian</a></li>
      <li><a href="http://www.atlassian.com/hosted/terms.jsp">Terms of Service</a></li>
      <li><a href="http://www.atlassian.com/about/privacy.jsp">Privacy</a></li>
      <li><a href="//bitbucket.org/site/master/issues/new">Report a Bug</a></li>
      <li><a href="http://confluence.atlassian.com/x/IYBGDQ">API</a></li>
      <li><a href="http://status.bitbucket.org/">Server Status</a></li>
    </ul>
    <ul id="social-nav">
      <li class="blog"><a href="http://blog.bitbucket.org">Bitbucket Blog</a></li>
      <li class="twitter"><a href="http://www.twitter.com/bitbucket">Twitter</a></li>
    </ul>
    <h5>We run</h5>
    <ul id="technologies">
      <li><a href="http://www.djangoproject.com/">Django 1.2.4</a></li>
      <li><a href="//bitbucket.org/jespern/django-piston/">Piston 0.2.3rc1</a></li>
      <li><a href="http://www.selenic.com/mercurial/">Hg 1.7.2</a></li>
      <li><a href="http://www.python.org">Python 2.7.0</a></li>
      <li>r6062:e0508678c572 | bitbucket02</li>
    </ul>
  </div>

  <script type="text/javascript" src="https://d1ga6s3xdhzo1c.cloudfront.net/7beb625ba6d9/js/8e1acf151111.js" charset="utf-8"></script>






  <script src="//cdn.optimizely.com/js/4079040.js"></script>
  <script type="text/javascript">
    var _gaq = _gaq || [];
    _gaq.push(['_setAccount', 'UA-2456069-3'], ['_trackPageview']);
  
    _gaq.push(['atl._setAccount', 'UA-6032469-33'], ['atl._trackPageview']);

        

    (function () {
        var ga = document.createElement('script');
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        ga.setAttribute('async', 'true');
        document.documentElement.firstChild.appendChild(ga);
    }());
  </script>

</body>
</html>
