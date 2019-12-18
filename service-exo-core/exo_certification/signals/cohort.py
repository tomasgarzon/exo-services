def cohort_post_save_handler(sender, instance, created, **kwargs):
    if created and instance.first_price_tier == 0:
        instance.first_price_tier = instance.price
        instance.save(update_fields=['first_price_tier'])
