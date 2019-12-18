class StripeWebhookMixin:

    def construct_stripe_payload_error(self, payment):
        return {
            'created': 1326853478,
            'livemode': 'false',
            'id': 'evt_00000000000000',
            'type': 'payment_intent.payment_failed',
            'object': 'event',
            'request': 'null',
            'pending_webhooks': 1,
            'api_version': '2019-05-16',
            'data': {
                'object': {
                    'id': payment.intent_id,
                    'object': 'payment_intent',
                    'amount': payment.amount_normalized,
                    'amount_capturable': 0,
                    'amount_received': 0,
                    'application': 0,
                    'application_fee_amount': 'null',
                    'canceled_at': 'null',
                    'cancellation_reason': 'null',
                    'capture_method': 'automatic',
                    'charges': {
                        'object': 'list',
                        'data': [],
                        'has_more': 'false',
                        'total_count': 0,
                        'url': '/v1/charges?payment_intent=pi_1EkF3jFDp6DWZAxpaurocAuS'
                    },
                    'client_secret': payment.intent_client_secret_id,
                    'confirmation_method': 'automatic',
                    'created': 1560279063,
                    'currency': payment.currency,
                    'customer': 'null',
                    'description': payment.concept,
                    'invoice': 'null',
                    'last_payment_error': {
                        'code': 'payment_intent_payment_attempt_failed',
                        'doc_url': 'https://stripe.com/docs/error-codes/payment-intent-payment-attempt-failed',
                        'message': 'The payment failed.',
                        'type': 'invalid_request_error'
                    },
                    'livemode': 'false',
                    'metadata': {},
                    'next_action': 'null',
                    'on_behalf_of': 'null',
                    'payment_method': 'null',
                    'payment_method_types': [
                        'card'
                    ],
                    'receipt_email': payment.email,
                    'review': 'null',
                    'shipping': 'null',
                    'source': 'null',
                    'statement_descriptor': 'null',
                    'status': 'requires_payment_method',
                    'transfer_data': 'null',
                    'transfer_group': 'null'
                }
            }
        }

    def construct_stripe_payload_success(self, payment):
        return {
            'id': 'evt_1EkTT3FDp6DWZAxpmVlXa48X',
            'object': 'event',
            'api_version': '2019-05-16',
            'created': 1560334448,
            'livemode': 'false',
            'pending_webhooks': 1,
            'request': {
                'id': 'req_82sVJLK4FxB9dv',
                'idempotency_key': 'null'
            },
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': payment.intent_id,
                    'object': 'payment_intent',
                    'amount': payment.amount_normalized,
                    'amount_capturable': 0,
                    'amount_received': payment.amount_normalized,
                    'application': 'null',
                    'application_fee_amount': 'null',
                    'canceled_at': 'null',
                    'cancellation_reason': 'null',
                    'capture_method': 'automatic',
                    'charges': {
                        'object': 'list',
                        'data': [
                            {
                                'id': 'ch_1EkTT2FDp6DWZAxpPxrIe1G9',
                                'object': 'charge',
                                'amount': payment.amount_normalized,
                                'amount_refunded': 0,
                                'application': 'null',
                                'application_fee': 'null',
                                'application_fee_amount': 'null',
                                'balance_transaction': 'txn_1EkTT2FDp6DWZAxpGQiv4Qlh',
                                'billing_details': {
                                    'address': {
                                        'city': 'null',
                                        'country': 'null',
                                        'line1': 'null',
                                        'line2': 'null',
                                        'postal_code': '42042',
                                        'state': 'null'
                                    },
                                    'email': payment.email,
                                    'name': payment.full_name,
                                    'phone': 'null'
                                },
                                'captured': 'true',
                                'created': 1560334448,
                                'currency': 'eur',
                                'customer': 'null',
                                'description': payment.concept,
                                'destination': 'null',
                                'dispute': 'null',
                                'failure_code': 'null',
                                'failure_message': 'null',
                                'fraud_details': {},
                                'invoice': 'null',
                                'livemode': 'false',
                                'metadata': {},
                                'on_behalf_of': 'null',
                                'order': 'null',
                                'outcome': {
                                    'network_status': 'approved_by_network',
                                    'reason': 'null',
                                    'risk_level': 'normal',
                                    'risk_score': 25,
                                    'seller_message': 'Payment complete.',
                                    'type': 'authorized'
                                },
                                'paid': 'true',
                                'payment_intent': payment.intent_id,
                                'payment_method': 'pm_1EkTT1FDp6DWZAxpC7XifuX2',
                                'payment_method_details': {
                                    'card': {
                                        'brand': 'visa',
                                        'checks': {
                                            'address_line1_check': 'null',
                                            'address_postal_code_check': 'pass',
                                            'cvc_check': 'pass'
                                        },
                                        'country': 'US',
                                        'exp_month': 4,
                                        'exp_year': 2024,
                                        'fingerprint': 'PTowkLICkyGY0ovA',
                                        'funding': 'credit',
                                        'last4': '4242',
                                        'three_d_secure': 'null',
                                        'wallet': 'null'
                                    },
                                    'type': 'card'
                                },
                                'receipt_email': payment.email,
                                'receipt_number': 'null',
                                'receipt_url': '',
                                'refunded': 'false',
                                'refunds': {
                                    'object': 'list',
                                    'data': [],
                                    'has_more': 'false',
                                    'total_count': 0,
                                    'url': '/v1/charges/ch_1EkTT2FDp6DWZAxpPxrIe1G9/refunds'
                                },
                                'review': 'null',
                                'shipping': 'null',
                                'source': 'null',
                                'source_transfer': 'null',
                                'statement_descriptor': 'null',
                                'status': 'succeeded',
                                'transfer_data': 'null',
                                'transfer_group': 'null'
                            }
                        ],
                        'has_more': 'false',
                        'total_count': 1,
                        'url': '/v1/charges?payment_intent=pi_1EkTRzFDp6DWZAxpwkMskFuW'
                    },
                    'client_secret': payment.intent_client_secret_id,
                    'confirmation_method': 'automatic',
                    'created': 1560334383,
                    'currency': 'eur',
                    'customer': 'null',
                    'description': payment.concept,
                    'invoice': 'null',
                    'last_payment_error': 'null',
                    'livemode': 'false',
                    'metadata': {},
                    'next_action': 'null',
                    'on_behalf_of': 'null',
                    'payment_method': 'pm_1EkTT1FDp6DWZAxpC7XifuX2',
                    'payment_method_types': [
                        'card'
                    ],
                    'receipt_email': payment.email,
                    'review': 'null',
                    'shipping': 'null',
                    'source': 'null',
                    'statement_descriptor': 'null',
                    'status': 'succeeded',
                    'transfer_data': 'null',
                    'transfer_group': 'null'
                }
            }
        }
