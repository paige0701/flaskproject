from inspect import getframeinfo, currentframe

from flask import flash
from flask import render_template, redirect, request, session
from flask import url_for
from flask_login import login_required
from flask_restful import Resource, fields, marshal_with

from apps import db
from apps.api_server.services.catalogue_service.models import CatalogueProduct, CatalogueCategory, \
    CatalogueProudctImage, \
    CatalogueProductType, CatalogueProductDetail, CatalogueCategoryDetail, CatalogueProductCart, CatalogueLineItem, \
    CatalogueProductAttribute, CatalogueAttributeAssociation
from apps.api_server.services.catalogue_service.form import ProductDetailForm, CartUpdateForm
from apps.api_server.services.catalogue_service.utils import make_category, make_category_detail, \
    make_category_with_detail, make_product, add_cart, update_cart
from apps.api_server.session_manager.checkout_session import CheckoutSessionData
from apps.web_server.services.product_service import product_blueprint
from flask_security import current_user


@product_blueprint.route('/list')
def product_list():
    category = 'ALL'
    cat = CatalogueProduct.query.all()
    jj = db.session.query(CatalogueProduct, CatalogueProductDetail).filter(
        CatalogueProduct.id == CatalogueProductDetail.product_code_id).all()

    return render_template('products/product_list.html', cat=cat, category=category, jj=jj)


@product_blueprint.route('/list/<int:num>')
def product_list_filter(num):
    categoryname = db.session.query(CatalogueCategory, CatalogueCategoryDetail).filter(
        CatalogueCategory.id == CatalogueCategoryDetail.category_code_id).filter(CatalogueCategory.id == num).first()

    jj = db.session.query(CatalogueProduct, CatalogueProductDetail, CatalogueCategory). \
        filter(CatalogueCategory.category_code == CatalogueProduct.category_id). \
        filter(CatalogueProduct.id == CatalogueProductDetail.product_code_id). \
        filter(CatalogueCategory.category_code == num).all()

    return render_template('products/product_list.html', categoryname=categoryname, jj=jj)


# product 상세 정보를 볼 수 있다
@product_blueprint.route('/detail/<int:num>')
def product_detail(num):

    product = CatalogueProduct.query.get(num)

    attribute = CatalogueAttributeAssociation.query.filter(CatalogueAttributeAssociation.product_id==num).all()
    p_form = ProductDetailForm()
    session['product_detail_no'] = num

    return render_template('products/product_detail.html', product=product, num=num, p_form=p_form, attribute=attribute)


# cart 버튼을 클릭했을때 카트에 저장이 되고 같은 페이지에 있는다
@product_blueprint.route('/add_to_cart/<int:num>', methods=['GET', 'POST'])
@login_required
def add_to_cart(num):
    if request.method == 'POST':
        p_form = ProductDetailForm(request.form)

        if not p_form.validate():
            detail = db.session.query(CatalogueProduct, CatalogueProductDetail).filter(
                CatalogueProductDetail.product_code_id == num).first()
            product = db.session.query(CatalogueProduct, CatalogueCategoryDetail). \
                filter(CatalogueProduct.id == CatalogueProductDetail.id). \
                filter(CatalogueProduct.id == num).first()

            session['product_detail_no'] = num
            return render_template('products/product_detail.html', p_form=p_form, detail=detail, product=product,
                                   num=num)

        else:
            add_cart(current_user.id, 'Open', num, request.form['quantity'])
            userid = current_user.id
            c_form = CartUpdateForm()
            k = CatalogueProductCart.query.filter(CatalogueProductCart.user_id == userid).first()

            return render_template('products/product_cart.html', k=k, c_form=c_form)
    else:
        return redirect(request.referrer)


# cart 테이블
@product_blueprint.route('/product_cart')
def product_cart():
    c_form = CartUpdateForm()

    if current_user.is_authenticated is True:
        userid = current_user.id
        k = CatalogueProductCart.query.filter(CatalogueProductCart.user_id == userid).first()

        return render_template('products/product_cart.html', c_form=c_form, k=k)
    else:
        return redirect(url_for('security.login'))


# cart 정보 업데이트
@product_blueprint.route('/cart_update', methods=['POST'])
def product_cart_update():
    for x in request.form:
        pp = CatalogueProduct.query.filter(CatalogueProduct.upc == x).all()
        for xx in pp:
            if current_user.is_authenticated is True:
                userid = current_user.id
                product = CatalogueProduct.query.filter(CatalogueProduct.id == xx.id).first()
                if int(request.form[x]) > int(product.quantity):
                    flash('We do not have that many :( ')
                    redirect(request.referrer)
                else:
                    update_cart(userid, 'Open', xx.id, request.form[x])
            else:
                return redirect(request.referrer)
    return redirect(url_for('product.product_cart'))


# 카트 정보 삭제
@product_blueprint.route('/cart_delete', methods=['POST'])
def product_delete():
    prr = request.form.getlist("chkboxpnum")
    if current_user.is_authenticated is True:
        userid = current_user.id
        k = CatalogueProductCart.query.filter(CatalogueProductCart.user_id == userid).first()

        k.remove_line_item(prr)
        db.session.commit()

    return redirect(request.referrer)
