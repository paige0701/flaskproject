

// Extra small screen / phone
//** Deprecated `@screen-xs` as of v3.0.1
@screen-xs:                  480px;
//** Deprecated `@screen-xs-min` as of v3.2.0
@screen-xs-min:              @screen-xs;
//** Deprecated `@screen-phone` as of v3.0.1
@screen-phone:               @screen-xs-min;

// Small screen / tablet
//** Deprecated `@screen-sm` as of v3.0.1
@screen-sm:                  768px;
@screen-sm-min:              @screen-sm;
//** Deprecated `@screen-tablet` as of v3.0.1
@screen-tablet:              @screen-sm-min;

// Medium screen / desktop
//** Deprecated `@screen-md` as of v3.0.1
@screen-md:                  992px;
@screen-md-min:              @screen-md;
//** Deprecated `@screen-desktop` as of v3.0.1
@screen-desktop:             @screen-md-min;

// Large screen / wide desktop
//** Deprecated `@screen-lg` as of v3.0.1
@screen-lg:                  1200px;
@screen-lg-min:              @screen-lg;
//** Deprecated `@screen-lg-desktop` as of v3.0.1
@screen-lg-desktop:          @screen-lg-min;

// So media queries don't overlap when required, provide a maximum
@screen-xs-max:              (@screen-sm-min - 1);
@screen-sm-max:              (@screen-md-min - 1);
@screen-md-max:              (@screen-lg-min - 1);

/* Large desktops and laptops (1200px~)*/
@media (min-width: @screen-lg-min) {

}

/* Landscape tablets and medium desktops (992px~1199px) */
@media (min-width: @screen-md-min) and (max-width: @screen-md-max) {

}

/* Portrait tablets and small desktops (768px~991px)*/
@media (min-width: @screen-sm-min) and (max-width: @screen-sm-max) {

}

/* Landscape phones and portrait tablets (~768px)*/
@media (min-width: @screen-xs-min) and (max-width: @screen-xs-max) {

}
------------------------------------------------------------------------

이건 사용 안함
/* Portrait phones and smaller (~479px) 사용 금지*/
//@media (max-width: 479px) {
//
//.kamper-header{
//    background-color:blue;
//  }
//}
