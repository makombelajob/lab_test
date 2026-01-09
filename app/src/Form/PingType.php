<?php

namespace App\Form;

use App\Entity\Ping;
use App\Entity\User;
use Symfony\Bridge\Doctrine\Form\Type\EntityType;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints as Assert;

class PingType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('hostname', null, [
                'constraints' => [
                    new Assert\NotBlank(message: 'Le hostname est obligatoire'),
                    new Assert\Length(
                        min: 3,
                        max: 100,
                        minMessage: 'Le hostname doit contenir au moins {{ limit }} caractères',
                        maxMessage: 'Le hostname ne peut pas dépasser {{ limit }} caractères'
                    ),
                    new Assert\Regex(
                        pattern: '/^[a-zA-Z0-9._-]+$/',
                        message: 'Le hostname contient des caractères invalides'
                    ),
                ],
                'attr' => [
                    'placeholder' => 'example.com',
                ]
            ])
            // ->add('ipAdress', null, [
            //     'constraints' => [
            //         new Assert\NotBlank(message: 'L’adresse IP est obligatoire'),
            //         new Assert\Ip(
            //             version: Assert\Ip::ALL,
            //             message: 'Adresse IP invalide'
            //         ),
            //     ],
            // ])
            // ->add('status', null, [
            //     'constraints' => [
            //         new Assert\NotBlank(message: 'Le statut est obligatoire'),
            //         new Assert\Choice(
            //             choices: ['up', 'down', 'unknown'],
            //             message: 'Statut invalide'
            //         ),
            //     ],
            // ])
            // ->add('user', EntityType::class, [
            //     'class' => User::class,
            //     'choice_label' => 'id',
            //     'placeholder' => 'Sélectionner un utilisateur',
            //     'constraints' => [
            //         new Assert\NotNull(message: 'Un utilisateur doit être sélectionné'),
            //     ],
            // ])
            // ->add('Envoyer', SubmitType::class)
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => Ping::class,
        ]);
    }
}
