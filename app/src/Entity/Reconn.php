<?php

namespace App\Entity;

use App\Repository\ReconnRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ReconnRepository::class)]
class Reconn
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $emailFound = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $userFound = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $linkFound = null;

    #[ORM\ManyToOne(inversedBy: 'reconn')]
    #[ORM\JoinColumn(nullable: false)]
    private ?Ping $ping = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getEmailFound(): ?string
    {
        return $this->emailFound;
    }

    public function setEmailFound(?string $emailFound): static
    {
        $this->emailFound = $emailFound;

        return $this;
    }

    public function getUserFound(): ?string
    {
        return $this->userFound;
    }

    public function setUserFound(?string $userFound): static
    {
        $this->userFound = $userFound;

        return $this;
    }

    public function getLinkFound(): ?string
    {
        return $this->linkFound;
    }

    public function setLinkFound(?string $linkFound): static
    {
        $this->linkFound = $linkFound;

        return $this;
    }

    public function getPing(): ?Ping
    {
        return $this->ping;
    }

    public function setPing(?Ping $ping): static
    {
        $this->ping = $ping;

        return $this;
    }
}
