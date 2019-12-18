# -*- coding: utf-8 -*-

"""
License boilerplate should be used here.
"""

# python 3 imports
from __future__ import absolute_import, unicode_literals

# python imports
import logging

# 3rd. libraries imports
from appconf import AppConf

from django.utils.text import slugify

# django imports
from django.conf import settings  # noqa

logger = logging.getLogger(__name__)


class CoreConfig(AppConf):

    CH_GENDER = (
        ('F', 'Female'),
        ('M', 'Male'),
    )

    CH_INDUSTRIES_LIST = [
        'Accommodations', 'Accounting', 'Advertising', 'Aerospace',
        'Agriculture & Agribusiness', 'Air Transportation', 'Aircraft',
        'Alcohol', 'Apparel & Accessories', 'Auto', 'Aviation', 'Banking',
        'Beauty & Cosmetics', 'Big Data', 'Biotechnology', 'Biotechnology',
        'Chemical', 'Communications', 'Computer', 'Construction',
        'Consulting', 'Consumer Products', 'Cosmetic', 'Cybersecurity',
        'Diamond',
        'Economy', 'Education', 'Electronics', 'Employment', 'Energy', 'Ethics',
        'Entertainment & Recreation',
        'Fashion', 'Financial Services', 'Food & Beverage', 'Future',
        'Glass', 'Health',
        'Hospitality',
        'Information',
        'Insurance', 'Inspiration', 'Internet of Things', 'Investment and Trading',
        'Journalism & News',
        'Legal Services', 'Life Sciences', 'Manufacturing',
        'Media & Broadcasting', 'Medical', 'Metal', 'Military',
        'Motion Pictures & Video', 'Music', 'Nanotechnology',
        'Neuroscience', 'Nuclear', 'Packaging', 'Paint & Coatings',
        'Oil and Gas',
        'Petrochemicals', 'Pharmaceutical', 'Plastics', 'Privacy', 'Private Spaceflight',
        'Publishing', 'Pulp & Paper', 'Rail', 'Real Estate', 'Recycling',
        'Retail', 'Robotics', 'Security', 'Service', 'Shipping', 'Shipyards',
        'Society', 'Solar', 'Space', 'Space-based Economy', 'Specialty Drugs',
        'Sporting Goods', 'Sports', 'Steel', 'Sustainability',
        'Telecommunications', 'Television', 'Textile', 'Tire', 'Tobacco', 'Toy', 'Transport',
        'Utilities',
        'Video Game',
        'Waste', 'Web Services',
    ]

    CH_INDUSTRIES = [(v1, v1) for v1 in CH_INDUSTRIES_LIST]
    CH_SLUG_INDUSTRIES = [
        (slugify(v1).replace('-', '_'), v1) for v1 in CH_INDUSTRIES_LIST
    ]

    EXO_ATTRIBUTES = [
        'Staff on Demand', 'Community & Crowd', 'Algorithms',
        'Leveraged Assets', 'Engagement', 'Interfaces', 'Dashboards',
        'Experimentation', 'Autonomy', 'Social Technologies',
    ]

    PREFIX_FILTER_SUMMARY = 'Filtered by: '
