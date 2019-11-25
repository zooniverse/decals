; Code by John Moustakas
; Original at https://raw.githubusercontent.com/moustakas/moustakas-projects/master/decals/decals_dr1_gallery.pro

pro make_html, htmlfile, pnglist=pnglist, npngcols=npngcols, $
  title=title, sample=sample1

    if (n_elements(npngcols) eq 0L) then npngcols = 3L

    html_path = file_dirname(htmlfile)
    png_path = html_path+'/png/'

    pngfiles = strtrim(sample1.object,2)+'.png'
    good = where(file_test(png_path+pngfiles) eq 1)
    sample = sample1[good]
    pngfiles = pngfiles[good]
    
    npngfiles = n_elements(pngfiles)
    
;    if (n_elements(pnglist) eq 0L) then begin
;       if keyword_set(or_jpeg) then $
;         pngfiles = [file_search(png_path+'*.png'),$
;         file_search(png_path+'*.jpg')] else $
;           pngfiles = file_search(png_path+'*.png')
;       npngfiles = n_elements(pngfiles)
;       if (npngfiles eq 0L) then begin
;          splog, 'No PNG files found in '+png_path
;          return
;       endif else pngfiles = file_basename(pngfiles)
;    endif else begin
;       pngfiles = pnglist
;       npngfiles = n_elements(pngfiles)
;;      tempfiles = file_search(png_path+pnglist,count=npngfiles)
;;      if (npngfiles ne n_elements(pnglist)) then begin
;;         splog, 'Some files in PNGLIST do not exist in '+png_path
;;         return
;;      endif
;    endelse

    if (not keyword_set(silent)) then splog, 'Found '+$
      string(npngfiles,format='(I0)')+' PNG files'

; generate the web page HTML page
    rootpngfiles = repstr(pngfiles,'.png','')
    nmenucols = npngcols

    if (not keyword_set(only_png)) then begin

       xwidth = string(fix(100/float(npngcols)),format='(I0)')
;      xwidth = string(fix(100/float(npscols)-npscols*3.0-npscols*15.0),format='(I0)')
;      xwidth = string(fix(100/float(npscols)-npscols*5.0),format='(I0)')
;      xwidth = '100'
       
       if (not keyword_set(silent)) then splog, 'Writing '+htmlfile
       
       openw, lun1, htmlfile,/get_lun
       printf, lun1, '<html>'
       printf, lun1, '<head>'
;      if (n_elements(title) eq 0L) then title = $
;        'Postscript Output for '+strupcase(htmlbase)
       printf, lun1, '<title>'+title+'</title>'
       printf, lun1, '<style type="text/css">'
       printf, lun1, '<!--'
       printf, lun1, 'body {'
       printf, lun1, '   color: white;'
       printf, lun1, '   background-color: black;'
       printf, lun1, '   text-align: center;'
       printf, lun1, '   border: 0;'
       printf, lun1, '   font-size: 100%;'
       printf, lun1, '   font-weight: bold;'
       printf, lun1, '}'
       printf, lun1, 'td {'
       printf, lun1, '   font-size: 100%;'
       printf, lun1, '   font-weight: bold;'
       printf, lun1, '   text-align: center;'
       printf, lun1, '}'
       printf, lun1, 'a {'
       printf, lun1, '   color: cyan;'
       printf, lun1, '   visited: cyan;'
       printf, lun1, '   text-decoration: none;'
       printf, lun1, '}'
       printf, lun1, '.center {'
       printf, lun1, '   text-align: center;'
       printf, lun1, '}'
       printf, lun1, '.left {'
       printf, lun1, '   text-align: left;'
       printf, lun1, '}'
       printf, lun1, '.smaller {'
       printf, lun1, '   font-size: 90%;'
       printf, lun1, '}'
       printf, lun1, 'h1 {color: gold;}'
       printf, lun1, '-->'
       printf, lun1, '</style>'
       printf, lun1, '</head>'
       printf, lun1, '<body>'
       printf, lun1, '</br>'
       printf, lun1, '<h1>'+title+'</h1>'
       printf, lun1, '</br>'

;      printf, lun1, '<br />'
;      printf, lun1, '<p class="left">This is text.</p>'
       printf, lun1, '<br />'
       printf, lun1, '<table align="center" cellpadding="5" border="1" cellspacing="5" width="100%">'
       printf, lun1, '<tbody>'

       for i = 0L, ceil(npngfiles/float(npngcols))-1 do begin
; images          
          printf, lun1, '<tr>'
          for j = 0L, npngcols-1 do begin
             indx = j + i*npngcols
             if (indx le npngfiles-1L) then begin
                printf, lun1, '<td width="'+xwidth+'%"><a href="png/'+pngfiles[indx]+'">'+$
                  '<img width="100%" align="center" valign="center" src="png/'+pngfiles[indx]+'"></a></td>'
             endif
          endfor
          printf, lun1, '</tr>'

; image captions          
          printf, lun1, '<tr>'
          for j = 0L, npngcols-1L do begin
             indx = j + i*npngcols
             if (indx le npngfiles-1L) then begin
;               printf, lun1, '<td width="'+xwidth+'%" class="center">'+string(j+1,format='(I0)')+':'+$
;                 string(i+1,format='(I0)')
                printf, lun1, '<td width="'+xwidth+'%" class="left">'+$
                  '<a target="_blank" href="http://legacysurvey.org/viewer/?layer=decals-dr1&ra='+$
                  strtrim(string(sample[indx].ra,format='(F12.4)'),2)+'&dec='+$
                  strtrim(string(sample[indx].dec,format='(F12.5)'),2)+'&zoom=14">'+$
                  strtrim(repstr(sample[indx].object,'-','/'),2)+'</a>'
;               printf, lun1, rootpngfiles[indx]+' <a href="'+htmlbase+'/'+pngfiles[indx]+'">png</a>'
                printf, lun1, '</td>'
             endif
          endfor
          printf, lun1, '</tr>'
          
       endfor 

       printf, lun1, '</tbody>'
       printf, lun1, '</table>'
       printf, lun1, '</body>'
       printf, lun1, '</html>'
       free_lun, lun1

    endif 

return
end


function get_template, nobj
    template = {object: '', ra: 0D, dec: 0D, $
      radius: 0.0, brickname: '', origin: ''}
return, replicate(template,nobj)
end

function get_ngc
; get and parse the catalog of NGC galaxies
    cat = mrdfits(getenv('CATALOGS_DIR')+'/ngc/ngc2000.fits',1)
    template = get_template(n_elements(cat))
    template.object = 'NGC'+strtrim(cat.ngcnum,2)
    template.ra = cat.ra
    template.dec = cat.dec
    template.radius = (cat.radius*60)>3.0
    template.origin = 'NGC'
; fix some coordinates
    fix = where(strmatch(template.object,'*2783*'))
    template[fix].ra = 15D*hms2dec('09h13m39.4s')
    template[fix].dec = hms2dec('+29d59m35s')
;; add in NGC2783b
;    template1 = get_template(1)
;    template1.object = 'NGC2783B'
;    template1.ra = 
;    template = [template,template1]
return, template
end

function get_abell
; get and parse the catalog of Abell clusters
    cat = mrdfits(getenv('IM_GITREPOS')+'/astrometry.net/catalogs/abell-all.fits',1)
    template = get_template(n_elements(cat))
    template.object = 'NGC'+strtrim(cat.ngcnum,2)
    template.ra = cat.ra
    template.dec = cat.dec
    template.radius = (cat.radius*60)>1.5
    template.origin = 'NGC'
return, template
end

function get_messier
; get and parse the catalog of Messier objects
    cat = rsex(getenv('CATALOGS_DIR')+'/ngc/messier.cat')
    template = get_template(n_elements(cat))
    template.object = 'M'+strtrim(cat.messier,2)
    template.ra = 15D*hms2dec(cat.ra)
    template.dec = hms2dec(cat.dec)
    template.radius = 3.0
    template.origin = 'Messier'
return, template
end

function get_rc3
; get and parse the catalog of RC3 objects
    cat = read_rc3()
    cat = cat[where(cat.d25_maj gt 1.0)]
    template = get_template(n_elements(cat))

    fix = where(strmatch(strtrim(cat.name,2),'A*'))
    cat[fix].name = strtrim(cat[fix].altname) ; replace A names with UGC 

    template.object = strcompress(cat.name,/remove)
    need = where(strcompress(template.object,/remove) eq '')
    if need[0] ne -1 then template[need].object = $
      strcompress(cat[need].altname,/remove)
    need = where(strcompress(template.object,/remove) eq '')
    if need[0] ne -1 then template[need].object = $
      strcompress(cat[need].pgc,/remove)

    template.ra = cat.ra
    template.dec = cat.dec
    template.radius = cat.d25_maj*3
    template.origin = 'RC3'
return, template
end
;Pegasus dIrr, ~800 kpc
;M_B = -11.2, 1.2d8 Msun in stars
;352.14208       14.746667 
;
;Leo A, ~800 kpc
;M_B = -11.6, 7d7 Msun in stars
;149.86000       30.746389

function resolve_duplicates, sample, debug=debug
; resolve duplicate objects
    grp = spheregroup(sample.ra,sample.dec,10D/3600D)
    ngrp = histogram(grp,reverse_indices=ri)
    ivec = ri[0:n_elements(ngrp)-1]
    
    oneobj = where(ngrp eq 1)   ; only one object - keep it!
    out_sample = sample[ri[ivec[oneobj]]]
    
; more than 1 object
    multobj = where(ngrp gt 1,nmult)
    for ii = 0L, nmult-1 do begin
       print, format='("Resolving duplicates ",I0,"/",I0, A10,$)', ii+1, nmult, string(13b)
       match = where(grp eq multobj[ii],nmatch)
       this = where(strtrim(sample[match].origin,2) eq 'RC3')
       if this[0] eq -1 then this = where(strtrim(sample[match].origin,2) eq 'Messier')
       if this[0] eq -1 then this = where(strtrim(sample[match].origin,2) eq 'NGC')
       out_sample = [out_sample,sample[match[this]]]
       if keyword_set(debug) then begin
          struct_print, sample[match] & struct_print, sample[match[this[0]]], /no_head
          print & cc = get_kbrd(1)
       endif
    endfor          
return, out_sample
end

function group_objects, sample, debug=debug
; group distinct objects which are near one another in the sky
    grp = spheregroup(sample.ra,sample.dec,2D/60D)
    ngrp = histogram(grp,reverse_indices=ri)
    ivec = ri[0:n_elements(ngrp)-1]
    
    oneobj = where(ngrp eq 1)   ; only one object - keep it!
    out_sample = sample[ri[ivec[oneobj]]]
    
; more than 1 object
    sample1 = get_template(1)
    multobj = where(ngrp gt 1,nmult)
    for ii = 0L, nmult-1 do begin
       print, format='("Grouping objects ",I0,"/",I0, A10,$)', ii+1, nmult, string(13b)
       match = where(grp eq multobj[ii],nmatch)
       obj = strtrim(sample[match].object,2)
       obj = obj[uniq(obj,sort(obj))]
       sample1.object = strjoin(obj,'-')
       sample1.ra = djs_mean(sample[match].ra)
       sample1.dec = djs_mean(sample[match].dec)
       sample1.origin = sample[match[0]].origin
       dra = (max(sample[match].ra)-min(sample[match].ra))/cos(sample[match[0]].dec*!dtor)
       ddec = max(sample[match].dec)-min(sample[match].dec)
       sample1.radius = ((dra>ddec)*60*1.5)>3.0
       out_sample = [out_sample,sample1]
       if keyword_set(debug) then begin
          struct_print, sample[match] & struct_print, sample1, /no_head
          print & cc = get_kbrd(1)
       endif
    endfor          
return, out_sample
end

pro decals_dr1_gallery, get_bricks=get_bricks, build_sample=build_sample, $
  get_cutouts=get_cutouts, make_png=make_png, html=html, debug=debug, $
  noclobber=noclobber
; jm15mar19siena - build some pretty pictures for DR1

    dr = 'dr1'

    dr1dir = decals_path(dr=dr)
;   gallerydir = decals_path(dr=dr,/gallery)
    gallerydir = '/project/projectdirs/cosmo/work/legacysurvey/gallery-dr1/'
;   gallerydir = getenv('HOME')+'/gallery-dr1/'
    if file_test(gallerydir,/dir) eq 0 then file_mkdir, gallerydir
    if file_test(gallerydir+'png',/dir) eq 0 then file_mkdir, gallerydir+'png'
    if file_test(gallerydir+'fits',/dir) eq 0 then file_mkdir, gallerydir+'fits'
    
    band = ['g','r','z']
    nband = n_elements(band)

    pixscale = 0.262D           ; [arcsec/pixel]
    nmosaic = 3600

; --------------------------------------------------
; figure out which bricks are done
    if keyword_set(get_bricks) then begin
       bricks = mrdfits(dr1dir+'decals-bricks-in-dr1-grz.fits',1)
       bb = bricks.brickname
       done = where(file_test(dr1dir+'coadd/'+strmid(bb,0,3)+'/'+$
         bb+'/decals-'+bb+'-model-g.fits.gz') and file_test(dr1dir+'coadd/'+strmid(bb,0,3)+'/'+$
         bb+'/decals-'+bb+'-model-r.fits.gz') and file_test(dr1dir+'coadd/'+strmid(bb,0,3)+'/'+$
         bb+'/decals-'+bb+'-model-z.fits.gz'))
       mwrfits, bricks[done], gallerydir+'decals-bricks-in-dr1-grz-done.fits', /create
    endif

; --------------------------------------------------
; build a sample of objects for the DR1 gallery
    if keyword_set(build_sample) then begin
       bricks = mrdfits(gallerydir+'decals-bricks-in-dr1-grz-done.fits',1)

       ngc = get_ngc()
       messier = get_messier()
       rc3 = get_rc3()
       cat = [ngc,messier,rc3]
       sample = resolve_duplicates(cat,debug=debug)
       splog, n_elements(sample), n_elements(cat)
       
; throw out some junk
       junk = where($
         strtrim(sample.object,2) eq 'NGC7670'$ ; no object at this position (together with NGC7668,7669
         ,comp=good)            ; 
       sample = sample[good]

; group the matches on 1 arcminute scales and get cutouts centered on
; the center of the group (to take care of multiple close systems)
       sample = group_objects(sample,debug=debug)
       nobj = n_elements(sample)

; find matching bricks
;      spherematch, sample.ra, sample.dec, bricks.ra, $
;        bricks.dec, 0.25/2, icat, ibrick ;, maxmatch=0
;      out_sample = sample[icat]
       delvarx, out_sample
       for ii = 0, nobj-1 do begin
          print, format='("Brick-matching object ",I0,"/",I0, A10,$)', ii+1, nobj, string(13b)
          this = where(sample[ii].ra gt bricks.ra1 and $
            sample[ii].ra lt bricks.ra2 and $
            sample[ii].dec gt bricks.dec1 and $
            sample[ii].dec lt bricks.dec2,nthis)
          if nthis gt 1 then message, 'Multiple matches!'
          if nthis eq 1 then begin
             sample[ii].brickname = bricks[this].brickname
             if n_elements(out_sample) eq 0L then out_sample = sample[ii] else $
               out_sample = [out_sample,sample[ii]]
          endif
       endfor
       out_sample = out_sample[reverse(sort(out_sample.dec))]
       struct_print, out_sample

       djs_plot, sample.ra, sample.dec, psym=6, xsty=3, ysty=3, symsize=0.5
       djs_oplot, bricks.ra, bricks.dec, psym=6, color='orange'
       djs_oplot, out_sample.ra, out_sample.dec, psym=7, color='blue'
       djs_oplot, messier.ra, messier.dec, psym=5, color='red', symsize=2

       im_mwrfits, out_sample, gallerydir+'gallery_sample.fits', /clobber
    endif 

; --------------------------------------------------
; find matching objects
    if keyword_set(get_cutouts) then begin
       sample = mrdfits(gallerydir+'gallery_sample.fits.gz',1)
       nobj = n_elements(sample)
; loop on each object (and demand 3-color photometry)
       oldfits = file_search(gallerydir+'fits/*.fits',count=nfits)
       if keyword_set(noclobber) eq 0 then if nfits ne 0 then file_delete, oldfits, /quiet
;      for ii = 0, 98 do begin
       for ii = 0L, nobj-1 do begin
          thisbrick = sample[ii].brickname
          http = 'http://legacysurvey.org/viewer/?layer=decals-dr1&ra='+$
            strtrim(string(sample[ii].ra,format='(F12.5)'),2)+'&dec='+$
            strtrim(string(sample[ii].dec,format='(F12.5)'),2)+'&zoom=14'
          splog, sample[ii].object, thisbrick
          print, http
          
          subdir = strmid(thisbrick,0,3)
          tractordir = dr1dir+'tractor/'+subdir+'/'
          coadddir = dr1dir+'coadd/'+subdir+'/'+thisbrick+'/'

          imfile = file_search(coadddir+'decals-'+thisbrick+'-image-'+band+'.fits',count=nfile)
          invvarfile = repstr(imfile,'-image','-invvar')
          modelfile = repstr(repstr(imfile,'-image','-model'),'.fits','.fits.gz')
;         if nfile ne nband then message, 'Missing some images!'
          if nfile eq nband then begin
             niceprint, imfile
;            /global/homes/i/ioannis/dr1/coadd/114/1146p215/decals-1146p215-image-z.fits
             
; save time by reading the images in all three bands
             image = fltarr(nmosaic,nmosaic,nband)
             invvar = image
             for ib = 0, nband-1 do begin
                image1 = readfits(imfile[ib],hdr,/silent)
                model = readfits(modelfile[ib],/silent)
                invvar[*,*,ib] = readfits(invvarfile[ib],ihdr,/silent)
                if image1[0] eq -1 or model[0] eq -1 then stop
                patch = where(reform(invvar[*,*,ib]) eq 0)
;               patch = where(image1 eq 0)
                if patch[0] ne -1 then image1[patch] = model[patch]
                image[*,*,ib] = image1
             endfor
             
             racen = djs_mean(sample[ii].ra)
             deccen = djs_mean(sample[ii].dec)
             width = sample[ii].radius/1.5
             adxy, hdr, racen, deccen, xx, yy
             x0 = (xx-width*60D/pixscale)
             x1 = (xx+width*60D/pixscale)
             y0 = (yy-width*60D/pixscale)
             y1 = (yy+width*60D/pixscale)
;            x0 = (xx-width*60D/pixscale)>0
;            x1 = (xx+width*60D/pixscale)<(nmosaic-1)
;            y0 = (yy-width*60D/pixscale)>0
;            y1 = (yy+width*60D/pixscale)<(nmosaic-1)

;             print, x0, x1, y0, y1
;             crop = max([0-x0,x1-(nmosaic-1),0-y0,y1-(nmosaic-1)])
;             x0 -= crop
;             x1 -= crop
;             y0 -= crop
;             y1 -= crop
;             print, x0, x1, y0, y1
;             if x0 lt 0 or y0 lt 0 or x1 gt (nmosaic-1) or y1 gt (nmosaic-1) then stop

             if x0 ge 0 and y0 ge 0 and x1 le (nmosaic-1) and y1 le (nmosaic-1) then begin
                fraczero = fltarr(nband)
                for ib = 0, nband-1 do begin
                   hextract, reform(image[*,*,ib]), hdr, $
                     newim1, newhdr1, x0, x1, y0, y1, /silent                   
                   hextract, reform(invvar[*,*,ib]), ihdr, $
                     newinvvar1, newihdr1, x0, x1, y0, y1, /silent                   
                   sz = size(newim1,/dim)
                   fraczero[ib] = total(newinvvar1 eq 0)/(1.0*sz[0]*sz[1])
;                  fraczero[ib] = total(newim1 eq 0)/(1.0*sz[0]*sz[1])
                   if ib eq 0 then begin
                      newim = newim1
                      newinvvar = newinvvar1
                      newhdr = newhdr1
                      newihdr = newihdr1
                   endif else begin
                      newim = [[[newim]],[[newim1]]]
                      newinvvar = [[[newinvvar]],[[newinvvar1]]]
                      newhdr = [[newhdr],[newhdr1]]
                      newihdr = [[newihdr],[newihdr1]]
                   endelse
                endfor                
; if more than 20% of the pixels are masked in any of the bands then
; throw out the object
                if total(fraczero ge 0.2) eq 0.0 then begin
                   for ib = 0, nband-1 do begin
                      outfile = gallerydir+'fits/'+strtrim(sample[ii].object,2)+'-'+band[ib]+'.fits'
                      splog, 'Writing '+outfile
                      mwrfits, reform(newim[*,*,ib]), outfile, reform(newhdr[*,ib]), /create
                      
;                  outfile = gallerydir+'fits/'+strtrim(sample[ii].object,2)+'-invvar-'+band[ib]+'.fits'
;                  splog, 'Writing '+outfile
;                  mwrfits, reform(newinvvar[*,*,ib]), outfile, reform(newihdr[*,ib]), /create
                   endfor
                endif 
             endif 
;print, ii & cc = get_kbrd(1)
          endif
       endfor 
    endif 

; --------------------------------------------------
; make the three-color images
    if keyword_set(make_png) then begin
       oldpng = file_search(gallerydir+'png/*.png',count=npng)
       if keyword_set(noclobber) eq 0 then if npng ne 0 then file_delete, oldpng, /quiet
       allfile = file_search(gallerydir+'fits/*-r.fits',count=nobj)
       for ii = 0, nobj-1 do begin
          name = repstr(file_basename(allfile[ii]),'-r.fits','')
;         pushd, gallerydir+'png'

; clean up previously created parameter files          
          file_delete, gallerydir+'png/'+['levels.txt', 'trilogyfilterlog.txt',$
            name+'.in',name+'_filters.txt'], /quiet
          
          infile = gallerydir+'png/'+name+'.in'
          openw, lun, infile, /get_lun
          printf, lun, 'B'
          printf, lun, file_search(gallerydir+'fits/'+name+'-g.fits')
          printf, lun, ''
          printf, lun, 'G'
          printf, lun, file_search(gallerydir+'fits/'+name+'-r.fits')
          printf, lun, ''
          printf, lun, 'R'
          printf, lun, file_search(gallerydir+'fits/'+name+'-z.fits')
          printf, lun, ''
          printf, lun, 'indir '+gallerydir+'fits/'
          printf, lun, 'outname '+gallerydir+'png/'+name
          printf, lun, 'noiselum 0.15'
;         printf, lun, 'scaling  '+gallerydir+'levels.txt'
          printf, lun, 'show 0'
          printf, lun, 'legend 0'
          printf, lun, 'testfirst 0'
          free_lun, lun

          cmd = 'python '+getenv('IMPY_DIR')+'/image/trilogy.py '+infile
          splog, cmd
          spawn, cmd, /sh
;         popd

; clean up the parameter files          
          file_delete, gallerydir+'png/'+['levels.txt', 'trilogyfilterlog.txt',$
            name+'.in',name+'_filters.txt'], /quiet
       endfor
    endif

; --------------------------------------------------
; build a simple web page
    if keyword_set(html) then begin
       sample = mrdfits(gallerydir+'gallery_sample.fits.gz',1)
       these = where(file_test(gallerydir+'png/'+strtrim(sample.object,2)+'.png'))

       title = 'DECaLS/DR1 Image Gallery'
       
       htmlfile = gallerydir+'index.html'
       make_html, htmlfile, npngcols=5, title=title, $
         pnglist=pngfiles, sample=sample[these]
    endif
    
stop    
    
return
end

