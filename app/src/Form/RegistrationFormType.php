<?php

namespace App\Form;

use App\Entity\User;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\CheckboxType;
use Symfony\Component\Form\Extension\Core\Type\PasswordType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\Extension\Core\Type\EmailType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints\IsTrue;
use Symfony\Component\Validator\Constraints\Length;
use Symfony\Component\Validator\Constraints\NotBlank;

class RegistrationFormType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('email', EmailType::class)

            ->add('firstName', TextType::class, [
                'constraints' => [
                    new NotBlank(['message' => 'Please enter your first name']),
                    new Length([
                        'max' => 50,
                        'maxMessage' => 'Your first name cannot be longer than {{ limit }} characters',
                    ]),
                ],
            ])

            ->add('lastName', TextType::class, [
                'constraints' => [
                    new NotBlank(['message' => 'Please enter your last name']),
                    new Length([
                        'max' => 50,
                        'maxMessage' => 'Your last name cannot be longer than {{ limit }} characters',
                    ]),
                ],
            ])

            ->add('category', ChoiceType::class, [
                'choices'  => [
                    'Personnel' => 'Personnel',
                    'Entreprise' => 'Entreprise'
                ],
                'placeholder' => 'Choose your category',
                'constraints' => [
                    new NotBlank(['message' => 'Please select a category']),
                ],
            ])

            ->add('agreeTerms', CheckboxType::class, [
                'mapped' => false,
                'label' => 'J\'accepte les conditions d\'utilisations et le respect envers autrui',
                'constraints' => [
                    new IsTrue([
                        'message' => 'You should agree to our terms.',
                    ]),
                ],
            ])

            ->add('plainPassword', PasswordType::class, [
                'mapped' => false,
                'attr' => ['autocomplete' => 'new-password'],
                'constraints' => [
                    new NotBlank([
                        'message' => 'Please enter a password',
                    ]),
                    new Length([
                        'min' => 6,
                        'minMessage' => 'Your password should be at least {{ limit }} characters',
                        'max' => 4096,
                    ]),
                ],
            ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => User::class,
        ]);
    }
}
